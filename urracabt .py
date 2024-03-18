#!/usr/bin/python3

import tkinter

from tkinter import Tk, Button, filedialog, \
     Label, Listbox, messagebox, StringVar, \
     Scrollbar, Text, Checkbutton, Menu, font, \
     LabelFrame, Entry, Radiobutton, PhotoImage, ttk
from tkinter.messagebox import askyesno
import os.path
import subprocess
import ast
import shutil
import gettext

root = Tk()

cron_ventana = None
ancho_pantalla = root.winfo_screenwidth()
alto_pantalla = root.winfo_screenheight()
ancho_ventana = 1217
alto_ventana = 495
medida_ancho_ajustada = round(ancho_pantalla / 2 - ancho_ventana / 2)
medida_alto_ajustada = round(alto_pantalla / 2 - alto_ventana / 2)
root.geometry(str(ancho_ventana) + "x" + str(alto_ventana) + "+" + str(medida_ancho_ajustada) + "+" + str(medida_alto_ajustada))
root.resizable(False, False)
root.iconphoto(True, PhotoImage(file="assets/urracabt.png"))
version = '1.24.3'
nombre_aplicacion = 'Urraca Backup Tool'
root.title(nombre_aplicacion + ' ' + 'v.' + version)
item_seleccionado = None
texto_etiqueta_mensaje_de_estado = StringVar()
texto_etiqueta_mensaje_de_estado_cron = StringVar()
opcion_delete_var = StringVar()
opcion_comprimir_var = StringVar()
modificacion_de_items = False
password_var = StringVar()
tipo_acceso_var = StringVar()
cron_minuto_var = StringVar()
cron_hora_var = StringVar()
cron_dia_mes_var = StringVar()
cron_mes_var = StringVar()
cron_dia_semana_var = StringVar()
cron_arroba_var = StringVar()
items_eliminados_lst = []
tmp_origen_lst = []
tmp_destino = ''
comandos_para_cron_lst = []
opcion_comprimir_inicial_str = None
opcion_delete_inicial_str = None
directorio_destino_inicial_str = None
puerto_remoto_inicial_str = None
password_var_inicial_str = None
tipo_acceso_var_inicial_str = None
color_negro = '#000'
color_rojo = '#f00'
idioma_seleccionado = ''
idioma_defecto = 'en'
appname = 'urracabt'
localedir = './locales'
i18n = gettext.translation(appname, localedir, fallback=True, languages=[idioma_defecto])
_ = i18n.gettext


def establece_idioma(idioma):

    global idioma_seleccionado, i18n, _
    idioma_seleccionado = idioma
    i18n = gettext.translation(appname, localedir, fallback=True, languages=[idioma_seleccionado])
    _ = i18n.gettext


def selecciona_idioma(idioma):
    
    global modificacion_de_items
    global idioma_seleccionado
    idioma_seleccionado = idioma
    messagebox.showinfo(title=nombre_aplicacion + ' ' + 'v.' + version,
                        message=_('Necesita guardar y reiniciar'))
    modificacion_de_items = True


def acerca_de():
    
    tiempo_espera_destruir = 6000
    acerca_de_win = Tk()
    acerca_de_win.resizable(False, False)
    acerca_de_win.title(nombre_aplicacion + ' ' + 'v.' + version)
    lbl_acerca_de_win = Label(master=acerca_de_win)
    lbl_acerca_de_win.configure(text=_('Urraca Backup Tool es un script en python'
                                       ' 3.10 y Tkinter para guardar\n y '
                                       'restaurar directorios y ficheros usando rsync.')
                                + _('\nPuede enviar comentarios, bugs '
                                    'y sugerencias para mejorarlo a\n\n')
                                + _('Danielsvenson@protonmail.com'))
    lbl_acerca_de_win.configure(font=(None, 12))
    lbl_acerca_de_win.pack(padx=35, pady=20)
    acerca_de_win.after(tiempo_espera_destruir, acerca_de_win.destroy)
    acerca_de_win.mainloop()


def recoge_valores_cron():
    texto_etiqueta_mensaje_de_estado_cron.set('')
    comandos_para_cron_lst.clear()
    if not cron_arroba_var.get() == '' and \
            (not cron_minuto_var.get() == ''
             or not cron_hora_var.get() == ''
             or not cron_dia_semana_var.get() == ''
             or not cron_mes_var.get() == ''
             or not cron_dia_mes_var.get() == ''):
        ventana_msg(_('Seleccione sólo un tipo de parámetro \n temporal'))
        return None
    parametros_tiempo_cron = ''
    if cron_arroba_var.get() == '':
        if not cron_minuto_var.get() == '':
            parametros_tiempo_cron += cron_minuto_var.get()
        else:
            parametros_tiempo_cron += '*'
        parametros_tiempo_cron += ' '
        if not cron_hora_var.get() == '':
            parametros_tiempo_cron += cron_hora_var.get()
        else:
            parametros_tiempo_cron += '*'
        parametros_tiempo_cron += ' '
        if not cron_dia_mes_var.get() == '':
            parametros_tiempo_cron += cron_dia_mes_var.get()
        else:
            parametros_tiempo_cron += '*'
        parametros_tiempo_cron += ' '
        if not cron_mes_var.get() == '':
            parametros_tiempo_cron += cron_mes_var.get()
        else:
            parametros_tiempo_cron += '*'
        parametros_tiempo_cron += ' '
        if not cron_dia_semana_var.get() == '':
            parametros_tiempo_cron += cron_dia_semana_var.get()
        else:
            parametros_tiempo_cron += '*'
        parametros_tiempo_cron += ' '
    else:
        parametros_tiempo_cron += cron_arroba_var.get()
    parametros_tiempo_cron = parametros_tiempo_cron.strip()
    if parametros_tiempo_cron == '* * * * *':
        ventana_msg(_('Debe especificar algún valor temporal'))
        return None
    procesa_datos_origen(True)
    err = False
    for elemento in comandos_para_cron_lst:
        elemento = parametros_tiempo_cron + ' ' + elemento
        comando = "(crontab -l 2>/dev/null; echo " + "'" + elemento + "'" + ") | crontab -"
        chequea_cmd = "crontab -l | grep " + "'" + elemento + "'"
        chequea_cmd = chequea_cmd.replace('*', '\\\\*')
        chequea_cmd = chequea_cmd.replace("'", '"')
        result = subprocess.Popen(chequea_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        err_decode = result.stderr.read().decode()
        if err_decode == '':
            err = False
        else:
            texto_etiqueta_mensaje_de_estado_cron.set(err_decode)
            err = True
        chequea_resultado = result.stdout.read().decode().strip()
        chequea_resultado_lst = chequea_resultado.split('\n')
        cont = False
        order_sent = False
        for elemento_lista_chequeo in chequea_resultado_lst:
            if elemento_lista_chequeo == elemento:
                item_origen=elemento.split(" ")
                signos_temporales = elemento.split('rsync')[0]
                mensaje = _('Ya existe en cron el elemento:\n') + signos_temporales + ' ' + item_origen[-2]   + _('\nSe omite')
                ventana_msg(mensaje)
                cont = True
            else:
                result = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                err_decode = result.stderr.read().decode()
                if err_decode == '':
                    err = False
                else:
                    texto_etiqueta_mensaje_de_estado_cron.set(err_decode)
                    err = True
                order_sent = True
        if cont:
            continue
    if not err and order_sent:
        msg_err = _('órdenes enviadas a cron correctamente')
        texto_etiqueta_mensaje_de_estado_cron.set(msg_err)


def ventana_msg(texto, ancho=400, alto=140):

    msg_ventana = tkinter.Toplevel(root)
    msg_ventana.wm_attributes('-topmost', True)
    ancho_ventana = ancho
    alto_ventana = alto
    tamano_ventana = str(ancho_ventana) + "x" + str(alto_ventana)
    msg_ventana.wm_geometry(tamano_ventana)
    msg_ventana.resizable(False, False)
    msg_ventana.title(nombre_aplicacion + ' ' + 'v.' + version)
    # Se ven el número de caracteres '\n en el mensaje.
    num_linea_siguiente = 0
    for i in texto:
        if '\n' in i:
            num_linea_siguiente += 1
    factor_altura_label = num_linea_siguiente*4.5
    msg_lbl = Label(msg_ventana, text=texto, font=(None, 12)).pack(pady=30-factor_altura_label)
    aceptar_btn = Button(msg_ventana, text=_('Aceptar'), command=lambda: msg_ventana.destroy(), font=(None, 12))
    aceptar_btn.place(x=160, y=87)

def programador_cron():

    from calendar import month_name, day_name
    cron_ventana = tkinter.Toplevel(root)
    cron_ventana.wm_attributes('-topmost', True)
    parametros_temporales_cron_lf = LabelFrame(cron_ventana, text=_('Parámetros de tiempo')
                                               , width=530, height=90, font=(None, 12))
    parametros_temporales_cron_lf.place(x=25, y=15)
    if idioma_seleccionado == 'en':
        cron_ventana.geometry('520x245')
    else:
        cron_ventana.geometry('545x255')

    cron_ventana.resizable(False, False)
    cron_ventana.title(nombre_aplicacion + ' ' + 'v.' + version)
    cron_minuto_lbl = Label(parametros_temporales_cron_lf, text=_('Minuto'),  font=(None, 12))
    cron_minuto_lbl.grid(row=0, column=0)
    cron_minuto_combobox = ttk.Combobox(parametros_temporales_cron_lf, textvariable=cron_minuto_var, width=5)
    cron_minuto_combobox['values'] = [m for m in range(0, 60)]
    cron_minuto_combobox.grid(row=1, column=0, padx=10, pady=10)
    cron_hora_lbl = Label(parametros_temporales_cron_lf, text=_('Hora'), font=(None, 12))
    cron_hora_lbl.grid(row=0, column=1)
    cron_hora_combobox = ttk.Combobox(parametros_temporales_cron_lf, textvariable=cron_hora_var, width=5)
    cron_hora_combobox['values'] = [m for m in range(0, 24)]
    cron_hora_combobox.grid(row=1, column=1, padx=0, pady=0)
    cron_dia_mes_lbl = Label(parametros_temporales_cron_lf, text=_('Día del mes'), font=(None, 12))
    cron_dia_mes_lbl.grid(row=0, column=2, padx=10, pady=0)
    cron_hora_combobox = ttk.Combobox(parametros_temporales_cron_lf, textvariable=cron_dia_mes_var, width=5)
    cron_hora_combobox['values'] = [m for m in range(1, 32)]
    cron_hora_combobox.grid(row=1, column=2, padx=10, pady=0)
    cron_mes_lbl = Label(parametros_temporales_cron_lf, text=_('Mes'), font=(None, 12))
    cron_mes_lbl.grid(row=0, column=3, padx=10, pady=0)
    cron_mes_combobox = ttk.Combobox(parametros_temporales_cron_lf, textvariable=cron_mes_var, width=5)
    cron_mes_combobox['values'] = [month_name[m][0:3] for m in range(1, 13)]
    cron_mes_combobox.grid(row=1, column=3, padx=10, pady=0)
    cron_dia_semana_lbl = Label(parametros_temporales_cron_lf, text=_('Día de la semana'), font=(None, 12))
    cron_dia_semana_lbl.grid(row=0, column=4, padx=10, pady=0)
    cron_dia_semana_combobox = ttk.Combobox(parametros_temporales_cron_lf, textvariable=cron_dia_semana_var, width=5)
    cron_dia_semana_combobox['values'] = [day_name[m][0:3] for m in range(0, 7)]
    cron_dia_semana_combobox.grid(row=1, column=4, padx=10, pady=0)
    cron_arroba_lbl = Label(cron_ventana, text=_('Cadenas de texto reservadas'), font=(None, 12))
    cron_arroba_lbl.place(x=25, y=129)
    cron_arroba_combobox = ttk.Combobox(cron_ventana, textvariable=cron_arroba_var, width=9)
    cron_arroba_combobox['values'] = ['@reboot', '@yearly',
                                      '@monthly', '@weekly', '@daily', '@midnight', '@hourly']
    if idioma_seleccionado == 'es':
        cron_arroba_combobox.place(x=275, y=135)
    else:
        cron_arroba_combobox.place(x=210, y=135)
    Label(cron_ventana, text=_('Línea de mensajes:'), font=(None, 12)).place(x=25, y=210)
    if idioma_seleccionado == 'es':
        x_pos = 250
    else:
        x_pos = 326
    Label(cron_ventana, text=_('Puede editar los desplegables manualmente'),
          font=(None, 9)).place(x=x_pos, y=102)
    aceptar_btn = Button(cron_ventana, text=_('Aceptar'), command=recoge_valores_cron, font=(None, 12))
    aceptar_btn.place(x=220, y=172)
    mensaje_de_estado_lbl_cron = Label(cron_ventana, textvariable=texto_etiqueta_mensaje_de_estado_cron,
                                       font=(font.Font(None, size=11, weight="bold")))
    texto_etiqueta_mensaje_de_estado_cron.set('')
    if idioma_seleccionado == 'es':
        x_pos = 185
    else:
        x_pos = 140
    mensaje_de_estado_lbl_cron.place(x=x_pos, y=210)


def crea_menus():
    
    menubar = Menu(root)
    menu_opciones = Menu(menubar, tearoff=0)
    menu_opciones.add_command(label=_('Español'), command=lambda: selecciona_idioma('es'))
    menu_opciones.add_command(label=_('Inglés'), command=lambda: selecciona_idioma('en'))
    menubar.add_cascade(label=_('Opciones de idioma'), menu=menu_opciones)
    menubar.add_command(label=_('Programador'), command=lambda: programador_cron())
    menubar.add_command(label=_('Acerca de'), command=lambda: acerca_de())
    root.config(menu=menubar)

log_txtbox_frame = tkinter.Frame(root)
dir_selected_lstbox_frame = tkinter.Frame(root)
left_buttons_frame = tkinter.Frame(root)

log_txtbox_frame.place(x=490, y=205, height=450, width=690)
dir_selected_lstbox_frame.place(x=35, y=55, height=215, width=430)
left_buttons_frame.place(x=28, y=338, height=100, width=430)

if os.path.isfile('urracabt.conf') == True:

    fichero_configuracion = open('urracabt.conf', 'r')
    items_fichero_configuracion = fichero_configuracion.readlines()
    fichero_configuracion.close()
    tmp_origen_lst = items_fichero_configuracion[0].split(',')
    tmp_destino = items_fichero_configuracion[1].strip()
    if not tmp_destino.find(':') == -1:
        opciones_dict = ast.literal_eval(tmp_destino)
        tmp_destino_ip = opciones_dict.get('destino')
        directorio_destino_inicial_str = tmp_destino_ip
        tmp_puerto_remoto = opciones_dict.get('puerto_remoto')
        puerto_remoto_inicial_str = tmp_puerto_remoto
        tipo_acceso_var.set(opciones_dict.get('tipo_acceso'))
        tipo_acceso_var_inicial_str = tipo_acceso_var.get()
        tmp_password = opciones_dict.get('password')
        password_var_inicial_str = opciones_dict.get('password')
    else:
        directorio_destino_inicial_str = tmp_destino

    opciones_dict = ast.literal_eval(items_fichero_configuracion[2])
    opcion_delete_var.set(opciones_dict.get('delete'))
    opcion_delete_inicial_str = opcion_delete_var.get()
    opciones_dict = ast.literal_eval(items_fichero_configuracion[3])
    opcion_comprimir_var.set(opciones_dict.get('comprimir_durante_copia'))
    opcion_comprimir_inicial_str = opcion_comprimir_var.get()
    idioma_seleccionado = items_fichero_configuracion[4]
    establece_idioma(idioma_seleccionado)
    crea_menus()
    
else:
    establece_idioma(idioma_defecto)
    crea_menus()
    messagebox.showinfo(title=nombre_aplicacion + ' ' +
                        'v.' + version, message=_('No existe el fichero de configuración\nElija directorios y') +
                        _(' ficheros de origen y destino para la copia\n' + _('No olvide guardar los cambios')))


def cuenta_atras(contador):

    if contador < 4:
        root.after(1000, cuenta_atras, contador + 1)
    if contador == 3:
        if not texto_etiqueta_mensaje_de_estado.get() == 'Copia finalizada' or\
                not texto_etiqueta_mensaje_de_estado.get() == 'Backup done':
            texto_etiqueta_mensaje_de_estado.set('')


def procesa_datos_origen(dry=False):

    if dry:
        global comandos_para_cron_lst
    else:
        log_txtbox.delete('1.0', tkinter.END)
    comprueba_existencia_en_origen()
    texto_etiqueta_mensaje_de_estado.set('')
    directorios_seleccionados_tupla = directorios_seleccionados_lstbox.get('0', 'end')
    directorio_destino = directorio_destino_txtbox.get('1.0', 'end').strip()
    if len(directorios_seleccionados_tupla) == 0 or len(directorio_destino) == 0:
        if len(directorios_seleccionados_tupla) == 0:
            messagebox.showinfo(title=nombre_aplicacion + ' ' + 'v.' + version,
                                message=_('No hay ficheros y/o directorios seleccionados para copiar'))
        if len(directorio_destino) == 0:
            messagebox.showinfo(title=nombre_aplicacion + ' ' + 'v.' + version,
                                message=_('No hay directorio de destino'))
        return None
    if not directorio_destino_txtbox.get('1.0', 'end').strip().find(':') == -1:
        if puerto_remoto_txtbox.get('1.0', 'end').strip() == '':
            messagebox.showinfo(title=nombre_aplicacion + ' ' + 'v.' + version,
                                message=_('Debe asignar un valor de puerto remoto para un destino remoto'))
            return None
        if tipo_acceso_var.get() == 'password' and password_var.get() == '':
            messagebox.showinfo(title=nombre_aplicacion + ' ' + 'v.' + version,
                                message=_('Debe asignar un valor de password para acceso con password'))
            return None
    if directorio_destino.find(':') == -1:
        if not os.path.exists(directorio_destino):
            messagebox.showinfo(title=nombre_aplicacion + ' ' + 'v.' + version,
                                message=_('No existe directorio de destino'))
            return None
    indice = 0
    for directorio_a_copiar in directorios_seleccionados_tupla:
        if directorios_seleccionados_lstbox.size() > indice:
            if not dry:
                directorios_seleccionados_lstbox.itemconfig(indice, bg="lightgrey")
            directorios_seleccionados_lstbox.update()
            indice = indice + 1
        if directorio_destino.find(':') == -1:
            comando_lst = ['rsync', '-avP', directorio_a_copiar, directorio_destino]
        else:
            if tipo_acceso_var.get() == 'password':
                passw = password_var.get()
                pto_remoto = puerto_remoto_txtbox.get('1.0', 'end').strip()
                comando_lst = ['rsync', '-avP', '-e', 'sshpass -p ' + passw + ' ssh -p ' + pto_remoto, directorio_a_copiar,
                           directorio_destino]
            else:
                pto_remoto = puerto_remoto_txtbox.get('1.0', 'end').strip()
                comando_lst = ['rsync', '-avP', '-e', ' ssh -p ' + pto_remoto,
                               directorio_a_copiar,
                               directorio_destino]
        if opcion_delete_var.get() == 'True':
            tmp = comando_lst[:]
            tmp.insert(2, '--delete')
            comando_lst = tmp.copy()
        if opcion_comprimir_var.get() == 'True':
            tmp = comando_lst[:]
            tmp[1] = tmp[1] + 'z'
            comando_lst = tmp.copy()
        comando_lst_str = ''
        for elemento in comando_lst:
            comando_lst_str += elemento.strip() + ' '
        if dry:
            comandos_para_cron_lst.append(comando_lst_str.strip())
            continue
        if not len(log_txtbox.get('1.0', tkinter.END)) > 0:
            log_txtbox.insert(tkinter.INSERT, '\n')
        texto_etiqueta_mensaje_de_estado.set(_('Ejecutando...'))
        log_txtbox.insert(tkinter.INSERT, _('Ejecutando ') + str(comando_lst_str))
        log_txtbox.insert(tkinter.INSERT, '\n')
        log_txtbox.update()
        result = subprocess.run(comando_lst, capture_output=True, text=True)
        if result.stderr != '':
            log_txtbox.insert(tkinter.INSERT, '\n' + 37*'*' + ' ERROR ' + 38*'*')
            log_txtbox.insert(tkinter.INSERT, result.stderr)
            log_txtbox.update()
            if 'Connection refused' in result.stderr:
                texto_etiqueta_mensaje_de_estado.set(_('Conexión rehusada'))
                messagebox.showerror(title=nombre_aplicacion + ' ' + 'v.' + version,
                                     message=_('Conexión rehusada Abandonando la copia'))
                return None
            if 'No route to host' in result.stderr:
                texto_etiqueta_mensaje_de_estado.set(_('No hay acceso al host'))
                messagebox.showerror(title=nombre_aplicacion + ' ' + 'v.' + version,
                                     message=_('No hay acceso al host Abandonando la copia'))
                return None
            if 'Permission denied' in result.stderr:
                texto_etiqueta_mensaje_de_estado.set(_('Permiso denegado'))
                messagebox.showerror(title=nombre_aplicacion + ' ' + 'v.' + version,
                                     message=_('Permiso denegado Abandonando la copia'))
                return None
            if 'Connection reset' in result.stderr:
                texto_etiqueta_mensaje_de_estado.set(_('Reset en la conexión'))
                messagebox.showerror(title=nombre_aplicacion + ' ' + 'v.' + version,
                                     message=_('Reset en la conexión Abandonando la copia'))
                return None
            texto_etiqueta_mensaje_de_estado.set(_('Error en el proceso'))
            messagebox.showerror(title=nombre_aplicacion + ' ' + 'v.' + version,
                                 message=_('Error en el proceso Abandonando la copia'))
            return None
        else:
            log_txtbox.insert(tkinter.INSERT, '\n')
            log_txtbox.insert(tkinter.INSERT, _('Sincronizando ')
                              + ' ' + directorio_a_copiar + ' --> '
                              + directorio_destino + '\n')
            log_txtbox.insert(tkinter.INSERT, result.stdout)
            log_txtbox.insert(tkinter.INSERT, '\n')
            log_txtbox.insert(tkinter.INSERT, 111*'-')
            log_txtbox.update()
        directorios_seleccionados_lstbox.itemconfig(indice-1, bg="white")
        texto_etiqueta_mensaje_de_estado.set(_(''))
    if not dry:
        texto_etiqueta_mensaje_de_estado.set(_('Copia finalizada'))
    if dry:
        return comandos_para_cron_lst

def guarda_lista_items_seleccionados():

    global modificacion_de_items, opcion_comprimir_inicial_str, opcion_delete_inicial_str, \
           directorio_destino_inicial_str, puerto_remoto_inicial_str, password_var_inicial_str, \
           tipo_acceso_var_inicial_str
    if not directorio_destino_txtbox.get('1.0', 'end').strip().find(':') == -1:
        if puerto_remoto_txtbox.get('1.0', 'end').strip() == '':
            messagebox.showinfo(title=nombre_aplicacion + ' ' + 'v.' + version,
                                message=_('Debe asignar un valor de puerto remoto para un destino remoto'))
        if tipo_acceso_var.get() == 'password' and password_var.get() == '':
            messagebox.showinfo(title=nombre_aplicacion + ' ' + 'v.' + version,
                                message=_('Debe asignar un valor de password para acceso con password'))
    if not (modificacion_de_items or not opcion_delete_inicial_str == opcion_delete_var.get() or
            not opcion_comprimir_inicial_str == opcion_comprimir_var.get()):
        texto_etiqueta_mensaje_de_estado.set(_('No hay cambios que guardar'))
        cuenta_atras(0)
        return None
    comprueba_existencia_en_origen()
    directorios_seleccionados_tupla = directorios_seleccionados_lstbox.get('0', 'end')
    directorio_destino = directorio_destino_txtbox.get('1.0', 'end').strip()
    if len(directorios_seleccionados_tupla) == 0 or len(directorio_destino) == 0:
        if len(directorios_seleccionados_tupla) == 0:
            messagebox.showinfo(title=nombre_aplicacion + ' ' + 'v.' + version,
                                message=_('No existen ficheros o directorios de origen para guardar'))
        if len(directorio_destino) == 0:
            messagebox.showinfo(title=nombre_aplicacion + ' ' + 'v.' + version,
                                message=_('No existe directorio de destino para guardar'))
        return None

    fichero_configuracion = open('urracabt.conf', 'w')
    for f in range(len(directorios_seleccionados_tupla)):
        fichero_configuracion.write(directorios_seleccionados_tupla[f])
        if f < len(directorios_seleccionados_tupla)-1:
            fichero_configuracion.write(',')
    fichero_configuracion.write('\n')
    if directorio_destino.find(':') == -1:
        fichero_configuracion.write(directorio_destino)
        fichero_configuracion.write('\n')
    else:
        puerto_remoto = puerto_remoto_txtbox.get('1.0', 'end').strip()
        password = password_entrybox.get().strip()
        tipo_acceso = tipo_acceso_var.get()
        _dict = ("{'destino':" + "'" + directorio_destino + "'"
                 + ',' + "'puerto_remoto':" + "'" + puerto_remoto + "'"
                 + ',' + "'tipo_acceso':" + "'" + tipo_acceso + "'"
                 + ',' + "'password':" + "'" + password + "'"
                 + "}")
        fichero_configuracion.write(_dict)
        fichero_configuracion.write('\n')
    if opcion_delete_var.get() == '':
        opcion_delete_var.set('False')
    _dict = "{'delete':" + "'" + opcion_delete_var.get() + "'" + "}"
    fichero_configuracion.write(_dict)
    fichero_configuracion.write('\n')
    if opcion_comprimir_var.get() == '':
        opcion_comprimir_var.set('False')
    _dict = "{'comprimir_durante_copia':" + "'" + opcion_comprimir_var.get() + "'" + "}"
    fichero_configuracion.write(_dict)
    fichero_configuracion.write('\n')
    if not idioma_seleccionado == '':
        fichero_configuracion.write(idioma_seleccionado)
    else:
        fichero_configuracion.write(idioma_defecto)
    fichero_configuracion.close()
    texto_etiqueta_mensaje_de_estado.set(_('La selección ha sido guardada'))
    cuenta_atras(0)

    modificacion_de_items = False
    opcion_comprimir_inicial_str = opcion_comprimir_var.get()
    opcion_delete_inicial_str = opcion_delete_var.get()
    directorio_destino_inicial_str = directorio_destino_txtbox.get('1.0', 'end').strip()
    puerto_remoto_inicial_str = puerto_remoto_txtbox.get('1.0', 'end').strip()
    password_var_inicial_str = password_var.get()
    tipo_acceso_var_inicial_str = tipo_acceso_var.get()


def comprueba_existencia_en_origen():
    
    global modificacion_de_items

    directorios_seleccionados_tupla = directorios_seleccionados_lstbox.get('0', 'end')
    for item_ in directorios_seleccionados_tupla:
        item_ = item_.strip()  # Se necesita para eliminar '\n' del último elemento de la lista.
        if not os.path.exists(item_):
            respuesta = askyesno(title=_('Confirmación'),
                                 message=_('El item de origen ')
                                 + item_ + _(' no existe\n')
                                 + _('¿Eliminar de la lista?'))
            if respuesta:
                indice_item = directorios_seleccionados_lstbox.get(0, 'end').index(item_)
                directorios_seleccionados_lstbox.delete(indice_item)
                modificacion_de_items = True
                directorio_destino = directorio_destino_txtbox.get('1.0', 'end').strip()
                item_ = item_[item_.rfind('/') + 1:]
                if os.path.exists(directorio_destino + '/' + item_):
                    respuesta = askyesno(title=_('Confirmación'),
                                         message=_('El item de origen ')
                                         + item_ + _(' existe en destino\n')
                                         + _('¿Desea eliminar en destino?'))
                    if respuesta:
                        if os.path.isfile(directorio_destino + '/' + item_):
                            os.remove(directorio_destino + '/' + item_)
                        if os.path.isdir(directorio_destino + '/' + item_):
                            shutil.rmtree(directorio_destino + '/' + item_)


def selecciona_directorios_origen():

    global modificacion_de_items
    directorio_origen = filedialog.askdirectory()
    directorio_en_listbox_bool = False
    for tmp in range(directorios_seleccionados_lstbox.size()):
        if directorio_origen == directorios_seleccionados_lstbox.get(tmp):
            directorio_en_listbox_bool = True
            messagebox.showinfo(title=nombre_aplicacion + ' ' + 'v.' + version,
                                message=_('El directorio ya existe en la selección'))
            break
    if not len(directorio_origen) == 0 and directorio_en_listbox_bool == False:
        directorios_seleccionados_lstbox.insert('end', directorio_origen)
        modificacion_de_items = True
        

def selecciona_ficheros_origen():

    global modificacion_de_items
    fichero_origen = filedialog.askopenfilename()
    fichero_en_listbox_bool = False
    for tmp in range(directorios_seleccionados_lstbox.size()):
        if fichero_origen == directorios_seleccionados_lstbox.get(tmp):
            fichero_en_listbox_bool = True
            messagebox.showinfo(title=nombre_aplicacion + ' ' + 'v.' + version,
                                message=_('El fichero ya existe en la selección'))
        break
    if not len(fichero_origen) == 0 and fichero_en_listbox_bool == False:
        directorios_seleccionados_lstbox.insert('end', fichero_origen)
        modificacion_de_items = True


def selecciona_destino():

    global modificacion_de_items
    directorio_destino = filedialog.askdirectory()
    if not len(directorio_destino) == 0:
        directorio_destino_txtbox.delete('1.0', 'end')
        directorio_destino_txtbox.insert('end', directorio_destino)
        modificacion_de_items = True
        
        
def elimina_items_seleccionados():
    
    global modificacion_de_items
    if not item_seleccionado is None:
        for i in directorios_seleccionados_lstbox.curselection():
            items_eliminados_lst.append(directorios_seleccionados_lstbox.get(i))
        
        directorios_seleccionados_lstbox.delete(item_seleccionado[0])
        modificacion_de_items = True

    else:
        messagebox.showinfo(title=nombre_aplicacion + ' ' + 'v.' + version,
                            message=_('No hay items seleccionados para eliminar'))


def comprueba_cambios_y_salir():
    
    modificacion_checkboxes = False
    if not opcion_comprimir_inicial_str == opcion_comprimir_var.get() or \
       not opcion_delete_inicial_str == opcion_delete_var.get():
        modificacion_checkboxes = True

    if modificacion_de_items or modificacion_checkboxes:
        respuesta = askyesno(title=_('Confirmación'),
                             message=_('Se han realizado modificaciones\n') + _('¿Guardar los cambios antes de salir?'))
        if respuesta:
            guarda_lista_items_seleccionados()
    respuesta = askyesno(title=_('Confirmación'),
                         message=_('¿Desea salir de Urraca Backup Tool?'))
    if respuesta:
        quit(0)


def cambia_color_label_delete():
    
    if opcion_delete_var.get() == 'True':
        option_delete_chkbtn.config(fg=color_rojo)
    else:
        option_delete_chkbtn.config(fg=color_negro)        


def callback(event):

    global item_seleccionado
    item_seleccionado = directorios_seleccionados_lstbox.curselection()


def limpia_log():

    log_txtbox.delete('1.0', tkinter.END)


def chequea_modificacion_destino(event):
    
    global modificacion_de_items
    if not directorio_destino_inicial_str == \
        directorio_destino_txtbox.get('1.0', 'end').strip():
        modificacion_de_items = True
    else:
        modificacion_de_items = False


def chequea_modificacion_puerto_remoto(event):

    if directorio_destino_txtbox.get('1.0', 'end').find(':') == -1:
        messagebox.showinfo(title=nombre_aplicacion + ' ' + 'v.' + version,
                            message=_('No se guardarán parámetros remotos para copia local'))
        puerto_remoto_txtbox.delete('1.0', tkinter.END)
        return None
    global modificacion_de_items
    if not puerto_remoto_inicial_str == \
        puerto_remoto_txtbox.get('1.0', 'end').strip():
        modificacion_de_items = True
    else:
        modificacion_de_items = False


def chequea_modificacion_password(event):

    if directorio_destino_txtbox.get('1.0', 'end').find(':') == -1:
        messagebox.showinfo(title=nombre_aplicacion + ' ' + 'v.' + version,
                            message=_('No se guardarán parámetros remotos para copia local'))
        password_var.set('')
        return None
    global modificacion_de_items
    if not password_var_inicial_str == password_var.get():
        modificacion_de_items = True
    else:
        modificacion_de_items = False

def chequea_modificacion_tipo_acceso(event):

    if directorio_destino_txtbox.get('1.0', 'end').find(':') == -1:
        messagebox.showinfo(title=nombre_aplicacion + ' ' + 'v.' + version,
                            message=_('No se guardarán parámetros remotos para copia local'))
        tipo_acceso_var.set('')
        return None

    global modificacion_de_items
    if not tipo_acceso_var_inicial_str == tipo_acceso_var.get():
        modificacion_de_items = True
    else:
        modificacion_de_items = False


opciones_remoto_lf = LabelFrame(root,  text=_('Opciones Remoto'), width=370, height=75, font=(None, 12))
opciones_remoto_lf.place(x=810, y=95)
tipo_acceso_lf = LabelFrame(root,  text=_('Tipo de Acceso Remoto'), width=288, height=60, font=(None, 12))
tipo_acceso_lf.place(x=490, y=100)
password_radiobtn = Radiobutton(
    tipo_acceso_lf,
    text='Password',
    value='password',
    variable=tipo_acceso_var,
    font=("None", 12))
password_radiobtn.place(x=2, y=4)
password_radiobtn.bind('<ButtonRelease>', chequea_modificacion_tipo_acceso)
clave_publica_radiobtn = Radiobutton(
    tipo_acceso_lf,
    text=_('Clave pública'),
    value='clave_publica',
    variable=tipo_acceso_var,
    font=("None", 12))
clave_publica_radiobtn.place(x=125, y=4)
clave_publica_radiobtn.bind('<ButtonRelease>', chequea_modificacion_tipo_acceso)
Label(root, text=_('Directorios y ficheros de origen seleccionados'),
      font=(None, 12)).place(x=35, y=25)
Label(root, text=_('Destino seleccionado (Local/Remoto)'), font=(None, 12)).place(x=490, y=25)
Label(root, text=_('Log del proceso'), font=(None, 12)).place(x=490, y=180)
Label(root, text=_('Línea de mensajes:'), font=(None, 12)).place(x=37, y=435)
Label(opciones_remoto_lf, text=_('Puerto Remoto'), font=(None, 11)).place(x=10, y=10)
Label(opciones_remoto_lf, text=_('Password'), font=(None, 11)).place(x=192, y=10)
mensaje_de_estado_lbl = Label(root, textvariable=texto_etiqueta_mensaje_de_estado,
                              font=(font.Font(None, size=11, weight="bold")))
if idioma_seleccionado == 'es':
    x_pos = 195
else:
    x_pos = 155
mensaje_de_estado_lbl.place(x=x_pos, y=435)
directorios_seleccionados_lstbox = Listbox(dir_selected_lstbox_frame, width=40, height=8, font=(None, 12), selectmode='browse')
directorios_seleccionados_lstbox.grid(row=0, column=0, sticky=tkinter.EW)
directorios_seleccionados_lstbox.bind('<<ListboxSelect>>', callback)
directorio_destino_txtbox = Text(root, height=1, width=39, font=(None, 12))
directorio_destino_txtbox.place(x=490, y=50)
directorio_destino_txtbox.bind('<KeyRelease>', chequea_modificacion_destino)
puerto_remoto_txtbox = Text(opciones_remoto_lf, height=1, width=5, font=(None, 11))
puerto_remoto_txtbox.place(x=128, y=8)
puerto_remoto_txtbox.bind('<KeyRelease>', chequea_modificacion_puerto_remoto)
log_txtbox = Text(log_txtbox_frame, height=11, width=67, font=(None, 12))
log_txtbox.grid(row=0, column=0, sticky=tkinter.EW)
password_entrybox = Entry(opciones_remoto_lf, width=8, show='*', textvariable=password_var, font=(None, 11))
password_entrybox.place(x=273, y=8)
password_entrybox.bind('<KeyRelease>', chequea_modificacion_password)
if not tmp_destino.find(':') == -1:
    puerto_remoto_txtbox.insert(tkinter.INSERT, tmp_puerto_remoto)
    password_entrybox.insert(0, tmp_password)
if not len(tmp_origen_lst) == 0:
    for item in range(len(tmp_origen_lst)):
        directorios_seleccionados_lstbox.insert('end', tmp_origen_lst[item].strip())
if not len(tmp_destino) == 0:
    if tmp_destino.find(':') == -1:
        directorio_destino_txtbox.insert(tkinter.INSERT, tmp_destino)
    else:
        directorio_destino_txtbox.insert(tkinter.INSERT, tmp_destino_ip)
scrollbar_0 = Scrollbar(dir_selected_lstbox_frame, orient='vertical',
                        command=directorios_seleccionados_lstbox.yview)
scrollbar_0.grid(row=0, column=1, sticky=tkinter.NS)
directorios_seleccionados_lstbox['yscrollcommand'] = scrollbar_0.set
scrollbar = Scrollbar(log_txtbox_frame, orient='vertical', command=log_txtbox.yview)
scrollbar.grid(row=0, column=1, sticky=tkinter.NS)
log_txtbox['yscrollcommand'] = scrollbar.set
option_delete_chkbtn = Checkbutton(root,
                                   text=_(' Eliminar en destino si ha sido borrado en origen'),
                                   font=(None, 12),
                                   variable=opcion_delete_var,
                                   onvalue='True',
                                   offvalue='False',
                                   command=cambia_color_label_delete)
option_delete_chkbtn.place(x=30, y=272)
option_comprimir_chkbtn = Checkbutton(root,
                                      text=_(' Comprimir durante la copia'),
                                      font=(None, 12),
                                      variable=opcion_comprimir_var,
                                      onvalue='True',
                                      offvalue='False')
option_comprimir_chkbtn.place(x=30, y=297)
cambia_color_label_delete()
(Button(left_buttons_frame, text=_('Elegir ficheros'), command=selecciona_ficheros_origen, font=(None, 12))
 .grid(row=0, column=0, padx=3, pady=3))
(Button(left_buttons_frame, text=_('Elegir directorios'), command=selecciona_directorios_origen, font=(None, 12))
 .grid(row=0, column=1, padx=3, pady=3))
(Button(left_buttons_frame, text=_('Eliminar'), command=elimina_items_seleccionados, font=(None, 12))
 .grid(row=0, column=3, padx=3, pady=3))
Button(root, text=_('Elegir destino local'), command=selecciona_destino, font=(None, 12)).place(x=910, y=45)
(Button(left_buttons_frame,  text=_('Guardar'), width=11, command=guarda_lista_items_seleccionados, font=(None, 12))
 .grid(row=1, column=0, padx=3, pady=3))
(Button(left_buttons_frame, text=_(' Iniciar copia '), width=14, command=procesa_datos_origen, font=(None, 12))
 .grid(row=1, column=1, padx=3, pady=3))
(Button(left_buttons_frame, text=_('Salir'), width=6, command=comprueba_cambios_y_salir, font=(None, 12))
 .grid(row=1, column=3, padx=3, pady=3))
(Button(log_txtbox_frame, text=_('Limpia Log'), width=8, command=limpia_log, font=(None, 12))
 .grid(row=1, column=0, padx=3, pady=9))

root.mainloop()
