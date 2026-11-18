
import os
import mysql.connector
from dotenv import load_dotenv
import json

load_dotenv()


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "job_trackers")
    )


def get_dashboard_counts():
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        tables = ["companies", "jobs", "applications", "contacts"]
        counts = {}

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) AS total FROM `{table}`")
            counts[table] = cursor.fetchone()["total"]

        cursor.close()
        return counts

    finally:
        connection.close()


def get_all_companies():
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                company_id,
                company_name,
                industry,
                website,
                city,
                state,
                notes
            FROM companies
            ORDER BY company_name
        """)

        companies = cursor.fetchall()
        cursor.close()

        return companies

    finally:
        connection.close()


def add_company(data):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO companies
                (company_name, industry, website, city, state, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data["company_name"],
            data["industry"],
            data["website"],
            data["city"],
            data["state"],
            data["notes"]
        ))

        connection.commit()
        cursor.close()

    finally:
        connection.close()


def get_company_by_id(company_id):
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT company_id, company_name, industry,
                   website, city, state, notes
            FROM companies
            WHERE company_id = %s
        """, (company_id,))

        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()


def update_company(company_id, data):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE companies
            SET company_name = %s,
                industry = %s,
                website = %s,
                city = %s,
                state = %s,
                notes = %s
            WHERE company_id = %s
        """, (
            data["company_name"],
            data["industry"],
            data["website"],
            data["city"],
            data["state"],
            data["notes"],
            company_id
        ))

        connection.commit()

    finally:
        cursor.close()
        connection.close()


def delete_company(company_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Check whether this company has related jobs.
        cursor.execute(
            "SELECT COUNT(*) FROM jobs WHERE company_id = %s",
            (company_id,)
        )
        job_count = cursor.fetchone()[0]

        # Check whether this company has related contacts.
        cursor.execute(
            "SELECT COUNT(*) FROM contacts WHERE company_id = %s",
            (company_id,)
        )
        contact_count = cursor.fetchone()[0]

        # Preserve companies that other records depend on.
        if job_count > 0 or contact_count > 0:
            return False

        cursor.execute(
            "DELETE FROM companies WHERE company_id = %s",
            (company_id,)
        )

        connection.commit()
        return cursor.rowcount > 0

    finally:
        cursor.close()
        connection.close()


def get_all_jobs():
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                j.job_id,
                j.company_id,
                j.job_title,
                j.job_description,
                j.salary_min,
                j.salary_max,
                j.job_type,
                j.job_url,
                j.date_posted,
                j.requirements,
                c.company_name
            FROM jobs j
            JOIN companies c
                ON j.company_id = c.company_id
            ORDER BY j.job_id DESC
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def add_job(data):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO jobs (
                company_id,
                job_title,
                job_description,
                salary_min,
                salary_max,
                job_type,
                job_url,
                date_posted,
                requirements
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data["company_id"],
            data["job_title"],
            data["job_description"],
            data["salary_min"],
            data["salary_max"],
            data["job_type"],
            data["job_url"],
            data["date_posted"],
            json.dumps(data["requirements"])
        ))

        connection.commit()

    finally:
        cursor.close()
        connection.close()


def get_job_by_id(job_id):
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                j.*,
                c.company_name
            FROM jobs j
            JOIN companies c ON j.company_id = c.company_id
            WHERE j.job_id = %s
        """, (job_id,))

        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()


def update_job(job_id, data):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE jobs
            SET company_id = %s,
                job_title = %s,
                job_description = %s,
                salary_min = %s,
                salary_max = %s,
                job_type = %s,
                job_url = %s,
                date_posted = %s,
                requirements = %s
            WHERE job_id = %s
        """, (
            data["company_id"],
            data["job_title"],
            data["job_description"],
            data["salary_min"],
            data["salary_max"],
            data["job_type"],
            data["job_url"],
            data["date_posted"],
            json.dumps(data["requirements"]),
            job_id
        ))

        connection.commit()

    finally:
        cursor.close()
        connection.close()


def delete_job(job_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM applications WHERE job_id = %s",
            (job_id,)
        )

        application_count = cursor.fetchone()[0]

        if application_count > 0:
            return False

        cursor.execute(
            "DELETE FROM jobs WHERE job_id = %s",
            (job_id,)
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:
        cursor.close()
        connection.close()


def get_all_applications():
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                a.application_id,
                a.job_id,
                a.application_date,
                a.status,
                a.resume_version,
                a.cover_letter_sent,
                a.interview_data,
                j.job_title,
                c.company_name
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            JOIN companies c ON j.company_id = c.company_id
            ORDER BY a.application_date DESC
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def add_application(data):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO applications (
                job_id,
                application_date,
                status,
                resume_version,
                cover_letter_sent,
                interview_data
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data["job_id"],
            data["application_date"],
            data["status"],
            data["resume_version"],
            data["cover_letter_sent"],
            json.dumps(data["interview_data"])
        ))

        connection.commit()

    finally:
        cursor.close()
        connection.close()


def get_application_by_id(application_id):
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                a.*,
                j.job_title,
                c.company_name
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            JOIN companies c ON j.company_id = c.company_id
            WHERE a.application_id = %s
        """, (application_id,))

        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()


def update_application(application_id, data):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE applications
            SET
                job_id = %s,
                application_date = %s,
                status = %s,
                resume_version = %s,
                cover_letter_sent = %s,
                interview_data = %s
            WHERE application_id = %s
        """, (
            data["job_id"],
            data["application_date"],
            data["status"],
            data["resume_version"],
            data["cover_letter_sent"],
            json.dumps(data["interview_data"]),
            application_id
        ))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        cursor.close()
        connection.close()


def delete_application(application_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM applications
            WHERE application_id = %s
        """, (application_id,))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        cursor.close()
        connection.close()


def get_all_contacts():
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                ct.contact_id,
                ct.company_id,
                ct.first_name,
                ct.last_name,
                ct.email,
                ct.phone,
                ct.job_title,
                ct.linkedin_url,
                ct.notes,
                c.company_name
            FROM contacts ct
            JOIN companies c ON ct.company_id = c.company_id
            ORDER BY ct.last_name, ct.first_name
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def add_contact(data):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO contacts (
                company_id,
                first_name,
                last_name,
                email,
                phone,
                job_title,
                linkedin_url,
                notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data["company_id"],
            data["first_name"],
            data["last_name"],
            data["email"],
            data["phone"],
            data["job_title"],
            data["linkedin_url"],
            data["notes"]
        ))

        connection.commit()

    finally:
        cursor.close()
        connection.close()


def get_contact_by_id(contact_id):
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM contacts
            WHERE contact_id = %s
        """, (contact_id,))

        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()


def update_contact(contact_id, data):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE contacts
            SET
                company_id = %s,
                first_name = %s,
                last_name = %s,
                email = %s,
                phone = %s,
                job_title = %s,
                linkedin_url = %s,
                notes = %s
            WHERE contact_id = %s
        """, (
            data["company_id"],
            data["first_name"],
            data["last_name"],
            data["email"],
            data["phone"],
            data["job_title"],
            data["linkedin_url"],
            data["notes"],
            contact_id
        ))

        connection.commit()
        return cursor.rowcount > 0

    finally:
        cursor.close()
        connection.close()


def delete_contact(contact_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM contacts
            WHERE contact_id = %s
        """, (contact_id,))

        connection.commit()
        return cursor.rowcount > 0

    finally:
        cursor.close()
        connection.close()
