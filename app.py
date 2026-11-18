import json
from ai_matcher import get_skill_equivalencies
from job_matcher import calculate_job_match

from flask import (
    Flask, render_template, request,
    redirect, url_for, flash
)

from database import (
    get_dashboard_counts,
    get_all_companies,
    add_company,
    get_company_by_id,
    update_company,
    delete_company,
    get_all_jobs,
    add_job as insert_job,
    get_job_by_id,
    update_job,
    delete_job,
    get_all_applications,
    add_application,
    get_application_by_id,
    update_application,
    delete_application,
    get_all_contacts,
    add_contact,
    get_contact_by_id,
    update_contact,
    delete_contact
)

app = Flask(__name__)
app.secret_key = "development-secret-key"


def get_company_form_data():
    return {
        "company_name": request.form.get("company_name", "").strip(),
        "industry": request.form.get("industry", "").strip(),
        "website": request.form.get("website", "").strip(),
        "city": request.form.get("city", "").strip(),
        "state": request.form.get("state", "").strip(),
        "notes": request.form.get("notes", "").strip()
    }


@app.route("/")
def dashboard():
    counts = get_dashboard_counts()
    return render_template("dashboard.html", counts=counts)


@app.route("/companies")
def companies():
    all_companies = get_all_companies()
    return render_template("companies.html", companies=all_companies)


@app.route("/companies/add", methods=["POST"], endpoint="add_company")
def add_company_route():
    data = get_company_form_data()

    if not data["company_name"]:
        flash("Company name is required.")
        return redirect(url_for("companies"))

    add_company(data)
    flash("Company added successfully!")

    return redirect(url_for("companies"))


@app.route("/companies/<int:company_id>/edit", methods=["GET", "POST"])
def edit_company(company_id):
    company = get_company_by_id(company_id)

    if company is None:
        flash("Company not found.")
        return redirect(url_for("companies"))

    if request.method == "POST":
        data = get_company_form_data()

        if not data["company_name"]:
            flash("Company name is required.")
            return redirect(
                url_for("edit_company", company_id=company_id)
            )

        update_company(company_id, data)
        flash("Company updated successfully!")

        return redirect(url_for("companies"))

    return render_template("edit_company.html", company=company)


@app.route("/companies/<int:company_id>/delete", methods=["POST"])
def delete_company_route(company_id):
    deleted = delete_company(company_id)

    if deleted:
        flash("Company deleted successfully!")
    else:
        flash(
            "This company cannot be deleted because it has "
            "associated jobs or contacts."
        )

    return redirect(url_for("companies"))



@app.route("/jobs")
def jobs():
    all_jobs = get_all_jobs()
    all_companies = get_all_companies()

    for job in all_jobs:
        job["display_requirements"] = format_job_requirements(
            job.get("requirements")
        )

    return render_template(
        "jobs.html",
        jobs=all_jobs,
        companies=all_companies
    )


@app.route("/jobs/add", methods=["POST"], endpoint="add_job")
def add_job_route():
    try:
        company_id = int(request.form.get("company_id"))

        salary_min = request.form.get("salary_min", "").strip()
        salary_max = request.form.get("salary_max", "").strip()

        requirements_text = request.form.get(
            "requirements", ""
        ).strip()

        requirements = [
            skill.strip()
            for skill in requirements_text.split(",")
            if skill.strip()
        ]

        data = {
            "company_id": company_id,
            "job_title": request.form.get("job_title", "").strip(),
            "job_description": request.form.get(
                "job_description", ""
            ).strip(),
            "salary_min": float(salary_min) if salary_min else None,
            "salary_max": float(salary_max) if salary_max else None,
            "job_type": request.form.get("job_type"),
            "job_url": request.form.get("job_url", "").strip(),
            "date_posted": request.form.get("date_posted") or None,
            "requirements": {
                "required_skills": requirements,
                "preferred_skills": []
            }
        }

        if not data["job_title"]:
            flash("Job title is required.")
            return redirect(url_for("jobs"))

        if data["job_type"] not in [
            "Full-time", "Part-time", "Contract", "Internship"
        ]:
            flash("Please select a valid job type.")
            return redirect(url_for("jobs"))

        if data["salary_min"] is not None and data["salary_min"] < 0:
            flash("Minimum salary cannot be negative.")
            return redirect(url_for("jobs"))

        if data["salary_max"] is not None and data["salary_max"] < 0:
            flash("Maximum salary cannot be negative.")
            return redirect(url_for("jobs"))

        if (
            data["salary_min"] is not None
            and data["salary_max"] is not None
            and data["salary_max"] < data["salary_min"]
        ):
            flash("Maximum salary cannot be lower than minimum salary.")
            return redirect(url_for("jobs"))

        insert_job(data)
        flash("Job added successfully!")

    except (ValueError, TypeError):
        flash("Please enter valid job information.")

    return redirect(url_for("jobs"))

def get_job_form_data():
    requirements_text = request.form.get("requirements", "")

    skills = [
        skill.strip()
        for skill in requirements_text.split(",")
        if skill.strip()
    ]

    salary_min = request.form.get("salary_min", "").strip()
    salary_max = request.form.get("salary_max", "").strip()

    return {
        "company_id": int(request.form.get("company_id")),
        "job_title": request.form.get("job_title", "").strip(),
        "job_description": request.form.get("job_description", "").strip(),
        "salary_min": float(salary_min) if salary_min else None,
        "salary_max": float(salary_max) if salary_max else None,
        "job_type": request.form.get("job_type"),
        "job_url": request.form.get("job_url", "").strip(),
        "date_posted": request.form.get("date_posted") or None,
        "requirements": {
            "required_skills": skills,
            "preferred_skills": []
        }
    }


def requirements_to_text(requirements):
    if not requirements:
        return ""

    if isinstance(requirements, str):
        try:
            requirements = json.loads(requirements)
        except json.JSONDecodeError:
            return requirements

    if isinstance(requirements, dict):
        skills = (
            requirements.get("required_skills", [])
            + requirements.get("preferred_skills", [])
        )
        return ", ".join(skills)

    if isinstance(requirements, list):
        return ", ".join(requirements)

    return ""


def format_job_requirements(requirements):
    if not requirements:
        return {}

    if isinstance(requirements, str):
        try:
            requirements = json.loads(requirements)
        except json.JSONDecodeError:
            return {"other": requirements}

    if isinstance(requirements, list):
        return {
            "required_skills": requirements
        }

    if isinstance(requirements, dict):
        return requirements

    return {}

@app.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
def edit_job(job_id):
    job = get_job_by_id(job_id)

    if job is None:
        flash("Job not found.")
        return redirect(url_for("jobs"))

    if request.method == "POST":
        try:
            data = get_job_form_data()

            if not data["job_title"]:
                flash("Job title is required.")
                return redirect(url_for("edit_job", job_id=job_id))

            if data["job_type"] not in [
                "Full-time", "Part-time", "Contract", "Internship"
            ]:
                flash("Please select a valid job type.")
                return redirect(url_for("edit_job", job_id=job_id))

            if (
                data["salary_min"] is not None
                and data["salary_min"] < 0
            ) or (
                data["salary_max"] is not None
                and data["salary_max"] < 0
            ):
                flash("Salary cannot be negative.")
                return redirect(url_for("edit_job", job_id=job_id))

            if (
                data["salary_min"] is not None
                and data["salary_max"] is not None
                and data["salary_max"] < data["salary_min"]
            ):
                flash("Maximum salary cannot be lower than minimum salary.")
                return redirect(url_for("edit_job", job_id=job_id))

            update_job(job_id, data)
            flash("Job updated successfully!")

            return redirect(url_for("jobs"))

        except (ValueError, TypeError):
            flash("Please enter valid job information.")
            return redirect(url_for("edit_job", job_id=job_id))

    return render_template(
        "edit_job.html",
        job=job,
        companies=get_all_companies(),
        requirements_text=requirements_to_text(job["requirements"])
    )


@app.route("/jobs/<int:job_id>/delete", methods=["POST"])
def delete_job_route(job_id):
    deleted = delete_job(job_id)

    if deleted:
        flash("Job deleted successfully!")
    else:
        flash(
            "This job cannot be deleted because it has "
            "associated applications."
        )

    return redirect(url_for("jobs"))


def get_application_form_data():
    interview_text = request.form.get("interview_data", "").strip()

    try:
        interview_data = json.loads(interview_text) if interview_text else None
    except json.JSONDecodeError:
        raise ValueError("Interview information must be valid JSON.")

    if interview_data is not None and not isinstance(interview_data, (dict, list)):
        raise ValueError("Interview information must be a JSON object or array.")

    return {
        "job_id": int(request.form.get("job_id")),
        "application_date": request.form.get("application_date"),
        "status": request.form.get("status"),
        "resume_version": request.form.get("resume_version", "").strip(),
        "cover_letter_sent": 1 if request.form.get("cover_letter_sent") else 0,
        "interview_data": interview_data
    }

@app.route("/applications")
def applications():
    all_applications = get_all_applications()
    all_jobs = get_all_jobs()

    return render_template(
        "applications.html",
        applications=all_applications,
        jobs=all_jobs
    )


@app.route("/applications/add", methods=["POST"])
def add_application_route():
    try:
        data = get_application_form_data()

        valid_statuses = [
            "Applied", "Screening", "Interview",
            "Offer", "Rejected", "Withdrawn"
        ]

        if not data["application_date"]:
            flash("Application date is required.")
            return redirect(url_for("applications"))

        if data["status"] not in valid_statuses:
            flash("Please select a valid application status.")
            return redirect(url_for("applications"))

        add_application(data)
        flash("Application added successfully!")

    except (ValueError, TypeError):
        flash("Please enter valid application information.")

    return redirect(url_for("applications"))


@app.route("/applications/<int:application_id>/edit", methods=["GET", "POST"])
def edit_application(application_id):
    application = get_application_by_id(application_id)

    if application is None:
        flash("Application not found.")
        return redirect(url_for("applications"))

    if request.method == "POST":
        try:
            data = get_application_form_data()

            valid_statuses = [
                "Applied", "Screening", "Interview",
                "Offer", "Rejected", "Withdrawn"
            ]

            # Allow an existing legacy status to remain unchanged.
            if data["status"] not in valid_statuses and data["status"] != application["status"]:
                flash("Please select a valid application status.")
                return redirect(url_for(
                    "edit_application",
                    application_id=application_id
                ))

            if not data["application_date"]:
                flash("Application date is required.")
                return redirect(url_for(
                    "edit_application",
                    application_id=application_id
                ))

            update_application(application_id, data)
            flash("Application updated successfully!")
            return redirect(url_for("applications"))

        except (ValueError, TypeError):
            flash("Please enter valid application information.")

    return render_template(
        "edit_application.html",
        application=application,
        jobs=get_all_jobs()
    )


@app.route("/applications/<int:application_id>/delete", methods=["POST"])
def delete_application_route(application_id):
    deleted = delete_application(application_id)

    if deleted:
        flash("Application deleted successfully!")
    else:
        flash("Application not found.")

    return redirect(url_for("applications"))


def get_contact_form_data():
    return {
        "company_id": int(request.form.get("company_id")),
        "first_name": request.form.get("first_name", "").strip(),
        "last_name": request.form.get("last_name", "").strip(),
        "email": request.form.get("email", "").strip() or None,
        "phone": request.form.get("phone", "").strip() or None,
        "job_title": request.form.get("job_title", "").strip(),
        "linkedin_url": request.form.get("linkedin_url", "").strip() or None,
        "notes": request.form.get("notes", "").strip() or None
    }


@app.route("/contacts")
def contacts():
    all_contacts = get_all_contacts()

    return render_template(
        "contacts.html",
        contacts=all_contacts,
        companies=get_all_companies()
    )


@app.route("/contacts/add", methods=["POST"])
def add_contact_route():
    try:
        data = get_contact_form_data()

        if not data["first_name"] or not data["last_name"]:
            flash("First and last name are required.")
            return redirect(url_for("contacts"))

        add_contact(data)
        flash("Contact added successfully!")

    except (ValueError, TypeError):
        flash("Please enter valid contact information.")

    return redirect(url_for("contacts"))


@app.route("/contacts/<int:contact_id>/edit", methods=["GET", "POST"])
def edit_contact(contact_id):
    contact = get_contact_by_id(contact_id)

    if contact is None:
        flash("Contact not found.")
        return redirect(url_for("contacts"))

    if request.method == "POST":
        try:
            data = get_contact_form_data()

            if not data["first_name"] or not data["last_name"]:
                flash("First and last name are required.")
                return redirect(url_for(
                    "edit_contact",
                    contact_id=contact_id
                ))

            update_contact(contact_id, data)
            flash("Contact updated successfully!")

            return redirect(url_for("contacts"))

        except (ValueError, TypeError):
            flash("Please enter valid contact information.")

    return render_template(
        "edit_contact.html",
        contact=contact,
        companies=get_all_companies()
    )


@app.route("/contacts/<int:contact_id>/delete", methods=["POST"])
def delete_contact_route(contact_id):
    deleted = delete_contact(contact_id)

    if deleted:
        flash("Contact deleted successfully!")
    else:
        flash("Contact not found.")

    return redirect(url_for("contacts"))



@app.route("/job-match", methods=["GET", "POST"])
def job_match():
    jobs = get_all_jobs()

    user_skills_text = ""
    matched_jobs = []
    searched = False
    used_equivalencies = []

    if request.method == "POST":
        searched = True
        user_skills_text = request.form.get("skills", "").strip()

        user_skills = [
            skill.strip()
            for skill in user_skills_text.split(",")
            if skill.strip()
        ]

        if user_skills:
            job_requirements = {}
            all_job_skills = set()

            for job in jobs:
                requirements = job.get("requirements")

                if isinstance(requirements, str):
                    try:
                        requirements = json.loads(requirements)
                    except json.JSONDecodeError:
                        requirements = None

                if isinstance(requirements, dict):
                    job_requirements[job["job_id"]] = requirements

                    all_job_skills.update(
                        requirements.get("required_skills", [])
                    )
                    all_job_skills.update(
                        requirements.get("preferred_skills", [])
                    )

            # One Gemini request for the entire search.
            ai_equivalencies = get_skill_equivalencies(
                user_skills,
                sorted(all_job_skills)
            )

            for job in jobs:
                requirements = job_requirements.get(job["job_id"])

                if not requirements:
                    continue

                job_skills = (
                    requirements.get("required_skills", [])
                    + requirements.get("preferred_skills", [])
                )

                job_skill_lookup = {
                    skill.strip().casefold()
                    for skill in job_skills
                    if isinstance(skill, str)
                }

                # Only apply equivalencies relevant to this job.
                job_equivalencies = [
                    item for item in ai_equivalencies
                    if item["job_skill"].casefold() in job_skill_lookup
                ]

                for item in job_equivalencies:
                    if item not in used_equivalencies:
                        used_equivalencies.append(item)

                result = calculate_job_match(
                    user_skills,
                    requirements,
                    [item["job_skill"] for item in job_equivalencies]
                )

                if result is not None:
                    matched_jobs.append({
                        **job,
                        **result
                    })

            matched_jobs.sort(
                key=lambda job: job["match_percentage"],
                reverse=True
            )

    return render_template(
        "job_match.html",
        matched_jobs=matched_jobs,
        user_skills_text=user_skills_text,
        searched=searched,
        total_jobs=len(jobs),
        ai_used=bool(used_equivalencies),
        ai_equivalencies=used_equivalencies
    )

if __name__ == "__main__":
    app.run(debug=True)