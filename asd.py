@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    user = get_user_by_username(username)

    if request.method == "POST":
        user["first_name"] = request.form["first_name"]
        user["last_name"] = request.form["last_name"]
        user["phone_number"] = request.form["phone_number"]
        user["email"] = request.form["email"]

        # Обробка завантаження аватарки
        if "avatar" in request.files:
            avatar_file = request.files["avatar"]
            if avatar_file.filename != "":
                if allowed_file(avatar_file.filename):
                    # Зберігаємо аватар як base64-encoded рядок
                    avatar_data = save_image_to_db(avatar_file)
                    user["avatar"] = avatar_data
                else:
                    return render_template("edit_profile.html", user=user, error="Недопустимий формат файлу")

        update_user_in_db(user)
        return redirect(url_for("profile"))

    # Завантаження аватара з бази даних
    if user.get("avatar"):
        user["avatar_url"] = f"data:image/png;base64,{user['avatar']}"
    else:
        user["avatar_url"] = url_for('static', filename='default_avatar.png')  # Шлях до стандартного аватара

    return render_template("edit_profile.html", user=user)