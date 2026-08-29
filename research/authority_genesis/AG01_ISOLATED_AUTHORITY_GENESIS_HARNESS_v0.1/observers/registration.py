def observe(run_id, registration_surface):
    v=registration_surface if registration_surface in {"TRUE","FALSE","UNRESOLVED"} else "UNRESOLVED"
    return {"run_id":run_id,"surface":"O_G","value":v}
