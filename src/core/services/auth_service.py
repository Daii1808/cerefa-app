ROLES_PERMISOS = {
    # ROLES DE MÉDICOS
    "medico": ["ver_fichas", "crear_fichas", "modificar_fichas", "registrar_fallecimiento", "dar_alta_medica"],
    "médico": ["ver_fichas", "crear_fichas", "modificar_fichas", "registrar_fallecimiento", "dar_alta_medica"],
    "medico veterinario": ["ver_fichas", "crear_fichas", "modificar_fichas", "registrar_fallecimiento", "dar_alta_medica"],
    "médico veterinario": ["ver_fichas", "crear_fichas", "modificar_fichas", "registrar_fallecimiento", "dar_alta_medica"],
    "medico veterinaria": ["ver_fichas", "crear_fichas", "modificar_fichas", "registrar_fallecimiento", "dar_alta_medica"],
    "médico veterinaria": ["ver_fichas", "crear_fichas", "modificar_fichas", "registrar_fallecimiento", "dar_alta_medica"],
    
    # ROLES DE TÉCNICOS
    "tecnico": ["ver_fichas", "crear_fichas", "modificar_fichas", "cambiar_a_rehabilitacion"],
    "técnico": ["ver_fichas", "crear_fichas", "modificar_fichas", "cambiar_a_rehabilitacion"],
    "tecnico veterinario": ["ver_fichas", "crear_fichas", "modificar_fichas", "cambiar_a_rehabilitacion"],
    "técnico veterinario": ["ver_fichas", "crear_fichas", "modificar_fichas", "cambiar_a_rehabilitacion"],
    
    # ROLES DE PRACTICANTES
    "practicante": ["ver_fichas", "crear_fichas", "modificar_fichas"]
}

def verificar_acceso_a_pantalla(rol_usuario, accion_solicitada):
    if not rol_usuario:
        print("--- DEBUG: Acceso denegado porque rol_usuario es None u vacío ---")
        return False
        
    rol_limpio = str(rol_usuario).lower().strip()
    
    print(f"--- DEBUG: Verificando | Rol limpio: '{rol_limpio}' | Acción solicitada: '{accion_solicitada}' ---")
    
    if rol_limpio not in ROLES_PERMISOS:
        print(f"--- DEBUG: El rol '{rol_limpio}' no existe en el diccionario de permisos ---")
        return False

    tiene_permiso = accion_solicitada in ROLES_PERMISOS[rol_limpio]
    print(f"--- DEBUG: ¿Tiene permiso?: {tiene_permiso} ---")
    
    return tiene_permiso