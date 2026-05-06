def attach_file(msg, file_path):
    try:
        with open(file_path, "rb") as file:
            file_name = file_path.split("\\")[-1].split("/")[-1]
            msg.add_attachment(
                file.read(),
                maintype="application",
                subtype="octet-stream",
                filename=file_name
            )
        return True
    except Exception as e:
        print("Error attaching file:", e)
        return False