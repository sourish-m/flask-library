from flask import render_template, request, redirect, url_for, flash
from models import db, Members
from app import app


@app.route("/members")
def memberspage():
    members = Members.query.order_by("member_id").all()
    return render_template("members.html", members=members)


@app.route("/add_member", methods=["GET", "POST"])
def add_member():
    if request.method == "POST":
        member_id = request.form.get("member_id")
        debt = request.form.get("debt")

        existing_member = Members.query.filter_by(member_id=member_id).first()

        if existing_member:
            flash("Member already exists!")
            return redirect(url_for("add_member"))

        new_member = Members(member_id=member_id, debt=debt)
        db.session.add(new_member)
        db.session.commit()

        flash("Member added successfully!")

    return render_template("add_member.html")


@app.route("/delete_member/<int:member_id>", methods=["POST"])
def delete_member(member_id):
    member = Members.query.get(member_id)

    if member:
        db.session.delete(member)
        db.session.commit()
        flash("Member deleted successfully!")
    else:
        flash("Member not found!")

    return redirect(url_for("memberspage"))


@app.route("/edit_member/<int:member_id>", methods=["GET", "POST"])
def edit_member(member_id):
    member = Members.query.get(member_id)
    if not member:
        flash("Member not found!")
        return redirect(url_for("memberspage"))

    if request.method == "POST":
        new_debt = request.form.get("debt")
        if int(new_debt) > 500:
            flash("Member debt cannot be greater than 500!")
        else:
            member.debt = new_debt
            db.session.commit()
            flash("Member details updated successfully!")
        return redirect(url_for("memberspage"))

    return render_template("edit_member.html", member=member)
