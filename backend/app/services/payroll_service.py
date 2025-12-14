from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.payroll import Employee, EmploymentContract, PayrollRun, PayrollSlip
from app.services.gemini import gemini_service
import json

class PayrollService:
    async def parse_contract(self, db: AsyncSession, employee_id: int, file_uri: str):
        """
        Extracts salary details from a contract PDF using Gemini.
        """
        # 1. Call AI
        prompt = """
        You are an HR Specialist.
        Extract salary details from this employment contract.
        Return JSON ONLY:
        {
            "basic_salary": float, 
            "housing_allowance": float, 
            "transport_allowance": float, 
            "other_allowance": float,
            "start_date": "YYYY-MM-DD",
            "iban": "SA..." (if present)
        }
        """
        response_text = await gemini_service.generate_answer(
            query=prompt,
            file_uris=[file_uri],
            role="hr",
            company="Unknown",
            system_instruction="Output JSON Only."
        )

        # 2. Parse JSON
        cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
        if "{" in cleaned_text:
            cleaned_text = cleaned_text[cleaned_text.find("{"):cleaned_text.rfind("}")+1]
        
        try:
            data = json.loads(cleaned_text)
        except:
             return None

        # 3. Update/Create Contract
        stmt = select(EmploymentContract).where(EmploymentContract.employee_id == employee_id)
        result = await db.execute(stmt)
        contract = result.scalars().first()
        
        from datetime import datetime
        start_date = None
        if data.get('start_date'):
            try:
                start_date = datetime.strptime(data['start_date'], "%Y-%m-%d")
            except:
                pass

        if not contract:
            contract = EmploymentContract(
                employee_id=employee_id,
                basic_salary=data.get('basic_salary', 0),
                housing_allowance=data.get('housing_allowance', 0),
                transport_allowance=data.get('transport_allowance', 0),
                other_allowance=data.get('other_allowance', 0),
                start_date=start_date,
                document_uri=file_uri
            )
            db.add(contract)
        else:
            contract.basic_salary = data.get('basic_salary', 0)
            contract.housing_allowance = data.get('housing_allowance', 0)
            contract.transport_allowance = data.get('transport_allowance', 0)
            contract.document_uri = file_uri
            if start_date: contract.start_date = start_date
        
        # Update Employee IBAN if found
        if data.get('iban'):
            stmt_emp = select(Employee).where(Employee.id == employee_id)
            res_emp = await db.execute(stmt_emp)
            emp = res_emp.scalars().first()
            if emp:
                emp.iban = data.get('iban')

        await db.commit()
        return contract

    async def generate_monthly_payroll(self, db: AsyncSession, tenant_id: int, month: int, year: int, attendance_data: dict):
        """
        Calculates payroll for all employees in tenant.
        attendance_data: { "employee_id_str": { "absent": 5 } }
        """
        # Create Run Header
        run = PayrollRun(tenant_id=tenant_id, month=month, year=year, status="Draft", total_payout=0)
        db.add(run)
        await db.commit()
        await db.refresh(run)

        # Fetch Employees with Contracts
        stmt = select(Employee).where(Employee.tenant_id == tenant_id)
        result = await db.execute(stmt)
        employees = result.scalars().all()

        total_payout = 0.0

        for emp in employees:
            # We need to fetch contract eagerly or via separate query
            stmt_c = select(EmploymentContract).where(EmploymentContract.employee_id == emp.id)
            res_c = await db.execute(stmt_c)
            contract = res_c.scalars().first()

            if not contract: continue

            # Calc
            gross = contract.basic_salary + contract.housing_allowance + contract.transport_allowance + contract.other_allowance
            
            daily_rate = gross / 30 if gross > 0 else 0
            
            emp_attendance = attendance_data.get(str(emp.id), {})
            absent_days = emp_attendance.get('absent', 0)
            
            deduction = daily_rate * absent_days
            net = gross - deduction
            
            # GOSI (Simple logic: 9.75% of Basic + Housing)
            # gosi_base = contract.basic_salary + contract.housing_allowance
            # gosi_deduction = gosi_base * contract.gosi_deduction_rate
            # net -= gosi_deduction 
            # (Skipping GOSI detail for MVP prompt, purely following user logic of Deduction = Absence)

            slip = PayrollSlip(
                run_id=run.id,
                employee_id=emp.id,
                gross_salary=gross,
                absent_days=absent_days,
                deduction_amount=deduction,
                net_salary=net
            )
            db.add(slip)
            total_payout += net

        run.total_payout = total_payout
        await db.commit()
        return run

    async def get_wps_csv(self, db: AsyncSession, run_id: int):
        stmt = select(PayrollSlip).where(PayrollSlip.run_id == run_id)
        result = await db.execute(stmt)
        slips = result.scalars().all()
        
        # Simple CSV format
        # Account,Amount,Name,Reference
        lines = ["IBAN,Amount,Name,Reference"]
        for slip in slips:
            # Need to fetch Employee Name/IBAN (lazy load might fail if strict async, so ensure join)
            # For MVP assume eager or separate fetch. Let's do separate fetch if needed.
            stmt_emp = select(Employee).where(Employee.id == slip.employee_id)
            res_emp = await db.execute(stmt_emp)
            emp = res_emp.scalars().first()
            
            if emp:
                lines.append(f"{emp.iban},{slip.net_salary},{emp.name},SALARY-{run_id}")
        
        return "\n".join(lines)

payroll_service = PayrollService()
