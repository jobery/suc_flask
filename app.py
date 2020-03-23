from flask import Flask,request,render_template,redirect,url_for,session,flash
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import secrets

from datetime import datetime

app = Flask(__name__)

conn = pymysql.connect(host='localhost',user='admin',passwd='admin',db='sucursal')

app.config['SECRET_KEY'] = secrets.token_urlsafe(10)

@app.route('/')
def inicio():    
    if not session.get('logged_in'):
        return login()
    else:
        return render_template('index.html') 

def format_datetime(value,format='%Y-%m-%d'):
    if value is None:
        return ""
    else:
        return value.strftime(format)

app.jinja_env.filters['datetime'] = format_datetime   

###-------------------------------------------------------- INI USUARIO -------------------------------------------------------------###
@app.route('/signup',methods=['POST','GET'])
def SignUp():
    if request.method == 'POST':
        nombre = str(request.form['user'])
        email = str(request.form['email'])
        password = generate_password_hash(str(request.form['password']))
        cursor = conn.cursor()
        cursor.execute("SELECT nombre,email FROM usuarios WHERE email = %s ",(email))
        usuario = cursor.fetchone()
        if usuario is not None:           
            flash("Correo ya Existe")
            return render_template('usuario/reg_usuario.html')
        else:
            cursor.execute("INSERT INTO usuarios(nombre,email,password,reg_ing)values(%s,%s,%s,NOW())",(nombre,email,password))
            conn.commit()            
            return redirect(url_for('login'))
    else:
        return render_template('usuario/reg_usuario.html')

@app.route('/login')
def login():
    return render_template('usuario/login.html')

@app.route('/usuario',methods=['POST','GET'])    
def usuario():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            nombre = str(request.form['user'])
            email = str(request.form['email'])
            password = generate_password_hash(str(request.form['password']))
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET nombre = %s,password = %s WHERE email = %s ",(nombre,password,email))
            conn.commit()
            session['logged_in'] = False
            session['nombre'] =  ''
            session['email'] =  '' 
            return redirect(url_for('login'))
        else:
            cursor = conn.cursor()
            cursor.execute("SELECT nombre,email FROM usuarios WHERE email = %s ",(session['email']))
            usuario = cursor.fetchone()
            contexto = {"nombre":usuario[0],"email":usuario[1]}
            if usuario is not None:
                return render_template('usuario/edi_usuario.html',form=contexto)
        

@app.route('/check',methods=['POST'])
def check():
    email = str(request.form['email'])
    password = str(request.form['password'])
    cursor = conn.cursor()
    cursor.execute("SELECT nombre,password FROM usuarios WHERE email = %s ",(email))
    usuario = cursor.fetchone()    
    if usuario is not None:
        session['logged_in'] = check_password_hash(usuario[1], password)
        if session['logged_in'] == False:
            session['nombre'] =  ''
            session['email'] =  ''            
            flash("Email o Password Incorrectos")
        else:
            session['nombre'] =  usuario[0]
            session['email'] =  email           
        return redirect(url_for('inicio'))
    else:
        flash("Email o Password Incorrectos")
        session['logged_in'] = False
        session['nombre'] =  ''
        session['email'] =  ''
        return redirect(url_for('inicio'))

@app.route('/salir')
def cerrar():
    session['logged_in'] = False
    session['nombre'] =  ''
    session['email'] =  ''     
    return redirect(url_for('inicio'))

###-------------------------------------------------------- FIN USUARIO -------------------------------------------------------------###
###--------------------------------------INICIO CLIENTES -------------------------------------------------###
@app.route('/clientes')
def clientes():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, correo, telefono, dui, nit, direccion FROM clientes ;")
        datos = cursor.fetchall()
        return render_template('clientes/lis_clientes.html',form=datos) 

@app.route('/cliente/agregar',methods=['POST'])    
def cliente_agregar():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            nombre = request.form['nombre']
            correo = request.form['correo']
            telefono = request.form['telefono']
            dui = request.form['dui']
            nit = request.form['nit']
            direccion = request.form['direccion']
            cursor = conn.cursor()
            cursor.execute("SELECT nit FROM clientes WHERE nit = %s ",(nit))            
            cliente = cursor.fetchone()
            if cliente is not None:           
                flash("Numero de Nit ya existe")
                redirect(url_for('clientes'))                
            else:
                cursor.execute("""INSERT INTO clientes(nombre, correo, telefono, dui, nit, direccion, activo, reg_ing)""" 
	            + """VALUES (%s, %s, %s, %s, %s, %s, 1, NOW())""",(nombre,correo,telefono,dui,nit,direccion))
                conn.commit()
                flash("Registro Guardado con Exito") 
            return redirect(url_for('clientes'))

@app.route('/cliente/editar/<int:id>',methods=['POST','GET'])
def cliente_editar(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        cursor = conn.cursor()
        if request.method == 'POST':
            nombre = request.form['nombre']
            correo = request.form['correo']
            telefono = request.form['telefono']
            dui = request.form['dui']
            nit = request.form['nit']
            direccion = request.form['direccion']            
            cursor.execute("""	UPDATE clientes SET
		    nombre= %s,correo=%s,telefono=%s,dui=%s,nit=%s,direccion=%s,activo=1,reg_mod=NOW()
	        WHERE id = %s """,(nombre,correo,telefono,dui,nit,direccion,id))
            conn.commit()
            flash("Registro Actualiazado con Exito")
            return redirect(url_for('clientes'))
        else:
            cursor.execute("SELECT id, nombre, correo, telefono, dui, nit, direccion FROM clientes WHERE id = %s ;",(id))
            cliente = cursor.fetchone()
            if cliente is not None:           
                return render_template('clientes/edi_cliente.html',form=cliente)               
            else:
                flash("Cliente no existe")
                return redirect(url_for('clientes'))

@app.route('/cliente/eliminar/<int:id>',methods=['POST','GET'])
def cliente_eliminar(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        cursor = conn.cursor()
        if request.method == 'POST':
            cursor.execute("DELETE FROM clientes WHERE id=%s ",(id))
            conn.commit()        
            flash("Registro Eliminado con Exito")
            return redirect(url_for('clientes'))
        else:
            cursor.execute("SELECT id,nombre FROM clientes WHERE id = %s ",(id))
            cliente = cursor.fetchone()            
            if cliente is not None:
                return render_template('clientes/eli_cliente.html',form=cliente)
            else:
                flash("Cliente no existe")
                return redirect(url_for('clientes'))  

###------------------------------------------FIN CLIENTES -------------------------------------------------###
###------------------------------------------INI VENDEDOR -------------------------------------------------###
@app.route('/vendedores')
def vendedores():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, correo, telefono, dui, nit, direccion FROM vendedores ;")
        datos = cursor.fetchall()
        return render_template('vendedores/lis_vendedores.html',form=datos)

@app.route('/vendedor/agregar',methods=['POST'])    
def vendedor_agregar():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            nombre = request.form['nombre']
            correo = request.form['correo']
            telefono = request.form['telefono']
            dui = request.form['dui']
            nit = request.form['nit']
            direccion = request.form['direccion']
            cursor = conn.cursor()
            cursor.execute("SELECT nit FROM vendedores WHERE nit = %s ",(nit))            
            cliente = cursor.fetchone()
            if cliente is not None:           
                flash("Numero de Nit ya existe")
                redirect(url_for('vendedores'))                
            else:
                cursor.execute("""INSERT INTO vendedores(nombre, correo, telefono, dui, nit, direccion, activo, reg_ing)""" 
	            + """VALUES (%s, %s, %s, %s, %s, %s, 1, NOW())""",(nombre,correo,telefono,dui,nit,direccion))
                conn.commit()
                flash("Registro Guardado con Exito") 
            return redirect(url_for('vendedores'))        


@app.route('/vendedor/editar/<int:id>',methods=['POST','GET'])
def vendedor_editar(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        cursor = conn.cursor()
        if request.method == 'POST':
            nombre = request.form['nombre']
            correo = request.form['correo']
            telefono = request.form['telefono']
            dui = request.form['dui']
            nit = request.form['nit']
            direccion = request.form['direccion']            
            cursor.execute("""	UPDATE vendedores SET
		    nombre= %s,correo=%s,telefono=%s,dui=%s,nit=%s,direccion=%s,activo=1,reg_mod=NOW()
	        WHERE id = %s """,(nombre,correo,telefono,dui,nit,direccion,id))
            conn.commit()
            flash("Registro Actualiazado con Exito")
            return redirect(url_for('vendedores'))
        else:
            cursor.execute("SELECT id, nombre, correo, telefono, dui, nit, direccion FROM vendedores WHERE id = %s ;",(id))
            cliente = cursor.fetchone()
            if cliente is not None:           
                return render_template('vendedores/edi_vendedor.html',form=cliente)               
            else:
                flash("Vendedor no existe")
                return redirect(url_for('vendedores'))


@app.route('/vendedor/eliminar/<int:id>',methods=['POST','GET'])
def vendedor_eliminar(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        cursor = conn.cursor()
        if request.method == 'POST':
            cursor.execute("DELETE FROM vendedores WHERE id=%s ",(id))
            conn.commit()        
            flash("Registro Eliminado con Exito")
            return redirect(url_for('vendedores'))
        else:
            cursor.execute("SELECT id,nombre FROM vendedores WHERE id = %s ",(id))
            cliente = cursor.fetchone()            
            if cliente is not None:
                return render_template('vendedores/eli_vendedor.html',form=cliente)
            else:
                flash("Vendedor no existe")
                return redirect(url_for('vendedores'))
###------------------------------------------FIN VENDEDOR -------------------------------------------------###
###------------------------------------------INI TIPOPRODUCTO -------------------------------------------------###
@app.route('/tiposproducto')
def tiposproducto():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM tipos_producto ;")
        datos = cursor.fetchall()
        return render_template('tiposproductos/lis_tiposproductos.html',form=datos) 

@app.route('/tipoproducto/agregar',methods=['POST'])    
def tipoproducto_agregar():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            nombre = request.form['nombre']
            cursor = conn.cursor()
            cursor.execute("SELECT nombre FROM tipos_producto WHERE nombre = %s ",(nombre))            
            tipopro = cursor.fetchone()
            if tipopro is not None:           
                flash("Tipo ya existe")
                redirect(url_for('tiposproducto'))                
            else:
                cursor.execute("""INSERT INTO tipos_producto(nombre, reg_ing)""" 
	            + """VALUES (%s, NOW())""",(nombre))
                conn.commit()
                flash("Registro Guardado con Exito") 
            return redirect(url_for('tiposproducto'))

@app.route('/tipoproducto/editar/<int:id>',methods=['POST','GET'])
def tipoproducto_editar(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        cursor = conn.cursor()
        if request.method == 'POST':
            nombre = request.form['nombre']            
            cursor.execute("""	UPDATE tipos_producto SET nombre= %s,reg_mod=NOW()
	        WHERE id = %s """,(nombre,id))
            conn.commit()
            flash("Registro Actualiazado con Exito")
            return redirect(url_for('tiposproducto'))
        else:
            cursor.execute("SELECT id, nombre FROM tipos_producto WHERE id = %s ;",(id))
            tipopro = cursor.fetchone()
            if tipopro is not None:           
                return render_template('tiposproductos/edi_tiposproducto.html',form=tipopro)               
            else:
                flash("Tipo no existe")
                return redirect(url_for('tiposproducto'))


@app.route('/tipoproducto/eliminar/<int:id>',methods=['POST','GET'])
def tipoproducto_eliminar(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        cursor = conn.cursor()
        if request.method == 'POST':
            cursor.execute("DELETE FROM tipos_producto WHERE id=%s ",(id))
            conn.commit()        
            flash("Registro Eliminado con Exito")
            return redirect(url_for('tiposproducto'))
        else:
            cursor.execute("SELECT id,nombre FROM tipos_producto WHERE id = %s ",(id))
            cliente = cursor.fetchone()            
            if cliente is not None:
                return render_template('tiposproductos/eli_tiposproducto.html',form=cliente)
            else:
                flash("Tipo no existe")
                return redirect(url_for('tiposproducto'))
###------------------------------------------INI TIPOPRODUCTO -------------------------------------------------###
###------------------------------------------INI PRODUCTOS -------------------------------------------------###
@app.route('/productos')
def productos():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM tipos_producto ;")
        tipos = cursor.fetchall()
        cursor.execute("SELECT id, nombre FROM formas_pago ;")
        formas = cursor.fetchall()
        cursor.execute(""" SELECT productos.id,productos.nombre,productos.tipo,tipos_producto.nombre AS nombre_tipo """ 
        + """ ,productos.costo,productos.precio,productos.existencia FROM productos LEFT JOIN tipos_producto """
        + """ ON productos.tipo = tipos_producto.id ORDER BY productos.id ;""")
        productos = cursor.fetchall()
        return render_template('productos/lis_productos.html',productos=productos,tipos=tipos,formas=formas) 


@app.route('/producto/agregar',methods=['POST'])    
def producto_agregar():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            nombre = request.form['nombre']
            tipo = request.form['tipo']
            costo = request.form['costo']
            precio = request.form['precio']
            cursor = conn.cursor()
            cursor.execute("SELECT nombre FROM productos WHERE nombre = %s ",(nombre))            
            producto = cursor.fetchone()
            if producto is not None:           
                flash("Nombre ya existe")
                redirect(url_for('productos'))                
            else:
                cursor.execute("""INSERT INTO productos(nombre, tipo, costo, precio, reg_ing)""" 
	            + """VALUES (%s, %s, %s, %s, NOW())""",(nombre,tipo,costo,precio))
                conn.commit()
                cursor.execute(""" SELECT id FROM productos WHERE nombre = %s and tipo = %s 
                AND costo = %s AND precio = %s ;""",(nombre,tipo,costo,precio))           
                producto = cursor.fetchone()             
                if producto is not None:
                    idproducto = producto[0]
                    for i in range(1,6):                                               
                        forma = request.form['tipoPrecio' + str(i)]
                        precio = request.form['precio' + str(i)]
                        prima = request.form['prima' + str(i)]
                        if forma != '' and float(precio) >= 0 and float(prima) >= 0:
                            cursor.execute("""INSERT INTO precios_producto(producto, forma, precio, prima, reg_ing)""" 
                            + """VALUES (%s, %s, %s, %s, NOW())""",(idproducto,forma,precio,prima))                            
                            conn.commit()
                flash("Registro Guardado con Exito") 
            return redirect(url_for('productos')) 


@app.route('/producto/editar/<int:id>',methods=['POST','GET'])
def producto_editar(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        cursor = conn.cursor()
        if request.method == 'POST':
            nombre = request.form['nombre']            
            tipo = request.form['tipo']  
            costo = request.form['costo']
            precio = request.form['precio']
            numdet = int(request.form['numdet'])    
            cursor.execute("""	UPDATE productos SET nombre= %s,tipo=%s,costo=%s,precio=%s,reg_mod=NOW()
	        WHERE id = %s """,(nombre,tipo,costo,precio,id))
            conn.commit()
            idproducto = id            
            for i in range(1,6):
                #if i <= numdet:
                iddet = request.form['id' + str(i)]                                                
                forma = request.form['tipoPrecio' + str(i)]
                precio = request.form['precio' + str(i)]
                prima = request.form['prima' + str(i)]
                print("iddet"+str(i)+" :")
                print(iddet)
                if iddet != '' and forma != '' and float(precio) >= 0 and float(prima) >= 0:
                    cursor.execute("""UPDATE precios_producto SET forma = %s,precio = %s, prima = %s""" 
                    + """ ,reg_mod = NOW() WHERE id = %s AND producto = %s ;  """,(forma,precio,prima,iddet,idproducto))                            
                    conn.commit()
                else:
                    if iddet == '' and forma != '' and float(precio) >= 0 and float(prima) >= 0:
                        cursor.execute("""INSERT INTO precios_producto(producto, forma, precio, prima, reg_ing)""" 
                        + """VALUES (%s, %s, %s, %s, NOW())""",(idproducto,forma,precio,prima))                            
                        conn.commit()
            flash("Registro Actualiazado con Exito")
            return redirect(url_for('productos'))
        else:
            cursor.execute("SELECT id, nombre FROM tipos_producto ;")
            tipos = cursor.fetchall()  
            cursor.execute("SELECT id, nombre FROM formas_pago ;")
            formas = cursor.fetchall()          
            cursor.execute("SELECT id, nombre,tipo,costo,precio,existencia FROM productos WHERE id = %s ;",(id))
            producto = cursor.fetchone()
            cursor.execute(""" SELECT tbl_a.id,tbl_a.producto,tbl_a.forma,tbl_b.nombre,tbl_a.precio,tbl_a.prima 
            FROM precios_producto AS tbl_a LEFT JOIN formas_pago AS tbl_b ON tbl_a.forma = tbl_b.id
            WHERE tbl_a.producto = %s ; """,(id))
            detalleprecios = cursor.fetchall()
            if producto is not None:           
                return render_template('productos/edi_producto.html',producto=producto,tipos=tipos,formas=formas,detalleprecios=detalleprecios)               
            else:
                flash("Producto no existe")
                return redirect(url_for('productos'))  


@app.route('/producto/eliminar/<int:id>',methods=['POST','GET'])
def producto_eliminar(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        cursor = conn.cursor()
        if request.method == 'POST':
            cursor.execute("DELETE FROM productos WHERE id = %s ;",(id))
            cursor.execute("DELETE FROM precios_producto WHERE producto = %s ;",(id))
            conn.commit()        
            flash("Registro Eliminado con Exito")
            return redirect(url_for('productos'))
        else:
            cursor.execute("SELECT id,nombre FROM productos WHERE id = %s ",(id))
            cliente = cursor.fetchone()            
            if cliente is not None:
                return render_template('productos/eli_producto.html',form=cliente)
            else:
                flash("Producto no existe")
                return redirect(url_for('productos'))
###------------------------------------------FIN PRODUCTOS -------------------------------------------------###
###------------------------------------------INI PROVEEDORES ----------------------_------------------------###
@app.route('/proveedores')
def proveedores():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, correo, telefono, dui, nit, direccion FROM proveedores ;")
        datos = cursor.fetchall()
        return render_template('proveedores/lis_proveedores.html',form=datos)

@app.route('/proveedor/agregar',methods=['POST'])    
def proveedor_agregar():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            nombre = request.form['nombre']
            correo = request.form['correo']
            telefono = request.form['telefono']
            dui = request.form['dui']
            nit = request.form['nit']
            direccion = request.form['direccion']
            cursor = conn.cursor()
            cursor.execute("SELECT nit FROM proveedores WHERE nit = %s ",(nit))            
            cliente = cursor.fetchone()
            if cliente is not None:           
                flash("Numero de Nit ya existe")
                redirect(url_for('proveedores'))                
            else:
                cursor.execute("""INSERT INTO proveedores(nombre, correo, telefono, dui, nit, direccion, activo, reg_ing)""" 
	            + """VALUES (%s, %s, %s, %s, %s, %s, 1, NOW())""",(nombre,correo,telefono,dui,nit,direccion))
                conn.commit()
                flash("Registro Guardado con Exito") 
            return redirect(url_for('proveedores'))        


@app.route('/proveedor/editar/<int:id>',methods=['POST','GET'])
def proveedor_editar(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        cursor = conn.cursor()
        if request.method == 'POST':
            nombre = request.form['nombre']
            correo = request.form['correo']
            telefono = request.form['telefono']
            dui = request.form['dui']
            nit = request.form['nit']
            direccion = request.form['direccion']            
            cursor.execute("""	UPDATE proveedores SET
		    nombre= %s,correo=%s,telefono=%s,dui=%s,nit=%s,direccion=%s,activo=1,reg_mod=NOW()
	        WHERE id = %s """,(nombre,correo,telefono,dui,nit,direccion,id))
            conn.commit()
            flash("Registro Actualiazado con Exito")
            return redirect(url_for('proveedores'))
        else:
            cursor.execute("SELECT id, nombre, correo, telefono, dui, nit, direccion FROM proveedores WHERE id = %s ;",(id))
            cliente = cursor.fetchone()
            if cliente is not None:           
                return render_template('proveedores/edi_proveedor.html',form=cliente)               
            else:
                flash("proveedor no existe")
                return redirect(url_for('proveedores'))


@app.route('/proveedor/eliminar/<int:id>',methods=['POST','GET'])
def proveedor_eliminar(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        cursor = conn.cursor()
        if request.method == 'POST':
            cursor.execute("DELETE FROM proveedores WHERE id=%s ",(id))
            conn.commit()        
            flash("Registro Eliminado con Exito")
            return redirect(url_for('proveedores'))
        else:
            cursor.execute("SELECT id,nombre FROM proveedores WHERE id = %s ",(id))
            cliente = cursor.fetchone()            
            if cliente is not None:
                return render_template('proveedores/eli_proveedor.html',form=cliente)
            else:
                flash("proveedor no existe")
                return redirect(url_for('proveedores'))
###------------------------------------------FIN PROVEEDORES ----------------------------------------------###
###------------------------------------------INI COMPRAS --------------------------------------------------###
@app.route('/compras')
def compras():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM proveedores ;")
        proveedores = cursor.fetchall()
        cursor.execute("SELECT id, nombre FROM productos ;")
        productos = cursor.fetchall()
        cursor = conn.cursor()
        cursor.execute("""SELECT TBL_A.id,TBL_A.documento,TBL_A.fecha,TBL_A.proveedor,TBL_B.nombre AS nombre_proveedor,TBL_A.total
	FROM compras AS TBL_A LEFT JOIN proveedores AS TBL_B ON TBL_A.proveedor = TBL_B.id ;""")
        compras = cursor.fetchall()
        return render_template('compras/lis_compras.html',compras=compras,proveedores=proveedores,productos=productos)

@app.route('/compra/agregar',methods=['POST'])    
def compra_agregar():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            fecha = request.form['fecha']
            documento = request.form['documento']
            proveedor = request.form['proveedor']
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM compras WHERE fecha = %s and documento = %s and proveedor = %s ",(fecha,documento,proveedor))            
            compra = cursor.fetchone()
            if compra == None:           
                               
                cursor.execute("""INSERT INTO compras(fecha, documento, proveedor, reg_ing)""" 
	            + """VALUES (%s, %s, %s, NOW())""",(fecha,documento,proveedor))
                conn.commit()

                cursor.execute("SELECT id FROM compras WHERE fecha = %s and documento = %s and proveedor = %s ",(fecha,documento,proveedor))           
                compra = cursor.fetchone()                
                if compra is not None:
                    idcompra = compra[0]
                    for i in range(1,6):                                               
                        producto = request.form['producto' + str(i)]
                        cantidad = request.form['cantidad' + str(i)]
                        precio = request.form['precio' + str(i)]
                        if producto != '' and float(cantidad) > 0 and float(precio) > 0.00:
                            cursor.execute("""INSERT INTO detalle_compra(compra, producto, cantidad, precio, reg_ing)""" 
                            + """VALUES (%s, %s, %s, %s, NOW())""",(idcompra,producto,cantidad,precio))
                            conn.commit()
                flash("Registro Guardado con Exito")
            else:
                flash("Compra ya existe")
                return redirect(url_for('compras')) 
            return redirect(url_for('compras')) 

@app.route('/compra/editar/<int:id>',methods=['POST','GET'])
def compra_editar(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        cursor = conn.cursor()
        if request.method == 'POST':
            fecha = request.form['fecha']
            documento = request.form['documento']
            proveedor = request.form['proveedor']
            cursor = conn.cursor()           
            cursor.execute("""	UPDATE compras SET
		    fecha= %s,documento=%s,proveedor=%s,reg_mod=NOW()
	        WHERE id = %s """,(fecha,documento,proveedor,id))
            conn.commit()
            idcompra = id
            numdet = int(request.form['numdet'])
            for i in range(1,6):
               if i <= numdet:
                    iddet = request.form['id' + str(i)] 
                    producto = request.form['producto' + str(i)]
                    cantidad = request.form['cantidad' + str(i)]
                    precio = request.form['precio' + str(i)]
                    if iddet != '' and producto != '' and float(cantidad) > 0 and float(precio) > 0.00:
                        cursor.execute("""UPDATE detalle_compra SET producto = %s,cantidad = %s,precio = %s,reg_mod = NOW() """ 
                        + """ WHERE id = %s AND compra = %s ;""",(producto,cantidad,precio,int(iddet),idcompra))
                        conn.commit()            
            flash("Registro Actualiazado con Exito")
            return redirect(url_for('compras'))
        else:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre FROM proveedores ;")
            proveedores = cursor.fetchall()
            cursor.execute("SELECT id, nombre FROM productos ;")
            productos = cursor.fetchall()
            cursor.execute("""SELECT TBL_A.id,TBL_A.fecha,TBL_A.documento,TBL_A.proveedor,TBL_B.nombre AS nombre_proveedor,TBL_A.total
            FROM compras AS TBL_A LEFT JOIN proveedores AS TBL_B ON TBL_A.proveedor = TBL_B.id  WHERE TBL_A.id = %s ;""",(id))
            compra = cursor.fetchall()
            cursor.execute("SELECT id,compra, producto, cantidad, precio FROM detalle_compra WHERE compra = %s",(id))
            detallecompra = cursor.fetchall()            
            if compra is not None:           
                return render_template('compras/edi_compra.html',compra=compra,proveedores=proveedores,productos=productos,detallecompra=detallecompra)               
            else:
                flash("Compra no existe")
                return redirect(url_for('compras'))

@app.route('/compra/eliminar/<int:id>',methods=['POST','GET'])
def compra_eliminar(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        cursor = conn.cursor()
        if request.method == 'POST':
            cursor.execute("DELETE FROM compras WHERE id = %s ",(id))            
            cursor.execute("DELETE FROM detalle_compra WHERE compra = %s",(id)) 
            conn.commit()       
            flash("Registro Eliminado con Exito")
            return redirect(url_for('compras'))
        else:
            cursor.execute("SELECT id,documento,fecha FROM compras WHERE id = %s ",(id))
            compra = cursor.fetchone()            
            if compra is not None:
                return render_template('compras/eli_compra.html',form=compra)
            else:
                flash("proveedor no existe")
                return redirect(url_for('compras'))                
###------------------------------------------FIN COMPRAS --------------------------------------------------###
###------------------------------------------INI CONSIGNAS ------------------------------------------------###
@app.route('/consignas')
def consignas():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM vendedores ;")
        vendedores = cursor.fetchall()
        cursor.execute("SELECT id, nombre FROM productos ;")
        productos = cursor.fetchall()
        cursor = conn.cursor()
        cursor.execute("""SELECT TBL_A.id,TBL_A.fecha,TBL_A.vendedor,TBL_B.nombre AS nombre_vendedor,TBL_A.total
	    ,IF(TBL_A.procesado=1,'SI','NO') AS procesado FROM consignas AS TBL_A LEFT JOIN vendedores AS TBL_B ON TBL_A.vendedor = TBL_B.id ;""")
        consignas = cursor.fetchall()
        return render_template('consignas/lis_consignas.html',consignas=consignas,vendedores=vendedores,productos=productos)

@app.route('/consigna/agregar',methods=['POST'])    
def consigna_agregar():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            fecha = request.form['fecha']
            vendedor = request.form['vendedor']
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM consignas WHERE fecha = %s and vendedor = %s ",(fecha,vendedor))            
            compra = cursor.fetchone()
            if compra == None:           
                               
                cursor.execute("""INSERT INTO consignas(fecha, vendedor, reg_ing)""" 
	            + """VALUES (%s, %s, NOW())""",(fecha,vendedor))
                conn.commit()

                cursor.execute("SELECT id FROM consignas WHERE fecha = %s and vendedor = %s ",(fecha,vendedor))           
                consigna = cursor.fetchone()                
                if consigna is not None:
                    idconsigna = consigna[0]
                    for i in range(1,6):                                               
                        producto = request.form['producto' + str(i)]
                        cantidad = request.form['cantidad' + str(i)]
                        if producto != '' and float(cantidad) > 0:
                            cursor.execute("""INSERT INTO detalle_consigna(consigna, producto, cantidad, reg_ing)""" 
                            + """VALUES (%s, %s, %s, NOW())""",(idconsigna,producto,cantidad))                            
                            conn.commit()
                flash("Registro Guardado con Exito")
            else:
                flash("Consigna ya existe")
                return redirect(url_for('consignas')) 
            return redirect(url_for('consignas')) 

@app.route('/consigna/editar/<int:id>',methods=['POST','GET'])
def consigna_editar(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        cursor = conn.cursor()
        if request.method == 'POST':
            fecha = request.form['fecha']
            proveedor = request.form['vendedor']
            cursor = conn.cursor()           
            cursor.execute("""	UPDATE consignas SET
		    fecha= %s,vendedor=%s,reg_mod=NOW()
	        WHERE id = %s """,(fecha,proveedor,id))
            conn.commit()
            idconsigna = id
            numdet = int(request.form['numdet'])
            for i in range(1,6):
               if i <= numdet:
                    iddet = request.form['id' + str(i)] 
                    producto = request.form['producto' + str(i)]
                    cantidad = request.form['cantidad' + str(i)]
                    if iddet != '' and producto != '' and float(cantidad) > 0:
                        cursor.execute("""UPDATE detalle_consigna AS tbl_a SET tbl_a.producto = %s,tbl_a.cantidad = %s,tbl_a.reg_mod = NOW() """ 
                        + """ WHERE tbl_a.id = %s AND tbl_a.consigna = %s ;""",(producto,cantidad,int(iddet),idconsigna))                        
                        conn.commit()                                 
            flash("Registro Actualiazado con Exito")
            return redirect(url_for('consignas'))
        else:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre FROM vendedores ;")
            vendedores = cursor.fetchall()
            cursor.execute("SELECT id, nombre FROM productos ;")
            productos = cursor.fetchall()
            cursor.execute("""SELECT TBL_A.id,TBL_A.fecha,TBL_A.vendedor,TBL_B.nombre AS nombre_vendedor,TBL_A.total
            ,IF(TBL_A.procesado=1,'SI','NO') AS procesado FROM consignas AS TBL_A LEFT JOIN vendedores AS TBL_B ON TBL_A.vendedor = TBL_B.id  WHERE TBL_A.id = %s ;""",(id))
            consigna = cursor.fetchall()
            cursor.execute("SELECT id,consigna, producto, cantidad FROM detalle_consigna WHERE consigna = %s",(id))
            detalleconsigna = cursor.fetchall()            
            if consigna is not None:           
                return render_template('consignas/edi_consigna.html',consigna=consigna,vendedores=vendedores,productos=productos,detalleconsigna=detalleconsigna)               
            else:
                flash("Consigna no existe")
                return redirect(url_for('consignas'))

@app.route('/consigna/eliminar/<int:id>',methods=['POST','GET'])
def consigna_eliminar(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        cursor = conn.cursor()
        if request.method == 'POST':
            cursor.execute("DELETE FROM consignas WHERE id = %s ",(id))            
            cursor.execute("DELETE FROM detalle_consigna WHERE consigna = %s",(id)) 
            conn.commit()       
            flash("Registro Eliminado con Exito")
            return redirect(url_for('consignas'))
        else:
            cursor.execute("SELECT id,fecha,vendedor FROM consignas WHERE id = %s ",(id))
            consigna = cursor.fetchone()            
            if consigna is not None:
                return render_template('consignas/eli_consigna.html',form=consigna)
            else:
                flash("Consigna no existe")
                return redirect(url_for('consignas')) 

@app.route('/consigna/procesar/<int:id>',methods=['POST','GET'])
def consigna_procesar(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        cursor = conn.cursor()
        if request.method == 'POST':
            cursor = conn.cursor()           
            cursor.execute("""	UPDATE consignas SET procesado = 1,reg_pro = NOW() WHERE id = %s """,(id))
            conn.commit()
            idconsigna = id
            numdet = int(request.form['numdet'])
            for i in range(1,6):
               if i <= numdet:
                    iddet = request.form['id' + str(i)] 
                    devolucion = request.form['devolucion' + str(i)]
                    if iddet != '' and float(devolucion) >= 0:
                        cursor.execute("""UPDATE detalle_consigna SET devolucion = %s,reg_dev = NOW() """ 
                        + """ WHERE id = %s AND consigna = %s ;""",(devolucion,int(iddet),idconsigna))
                        conn.commit()            
            flash("Registro Procesado con Exito")
            return redirect(url_for('consignas'))
        else:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre FROM vendedores ;")
            vendedores = cursor.fetchall()
            cursor.execute("SELECT id, nombre FROM productos ;")
            productos = cursor.fetchall()
            cursor.execute("""SELECT TBL_A.id,TBL_A.fecha,TBL_A.vendedor,TBL_B.nombre AS nombre_vendedor,TBL_A.total
            ,IF(TBL_A.procesado=1,'SI','NO') AS procesado FROM consignas AS TBL_A LEFT JOIN vendedores AS TBL_B ON TBL_A.vendedor = TBL_B.id  WHERE TBL_A.id = %s ;""",(id))
            consigna = cursor.fetchall()
            cursor.execute("SELECT id,consigna, producto, cantidad,devolucion FROM detalle_consigna WHERE consigna = %s",(id))
            detalleconsigna = cursor.fetchall()            
            if consigna is not None:           
                return render_template('consignas/pro_consigna.html',consigna=consigna,vendedores=vendedores,productos=productos,detalleconsigna=detalleconsigna)               
            else:
                flash("Consigna no existe")
                return redirect(url_for('consignas'))
###------------------------------------------FIN CONSIGNAS ------------------------------------------------###
###------------------------------------------INI FORMAPAGO -------------------------------------------------###
#--- LISTADO FORMAPAGO ---#
@app.route('/formaspago')
def formaspago():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre,dias FROM formas_pago ;")
        datos = cursor.fetchall()
        return render_template('formaspago/lis_formaspago.html',form=datos) 

#--- NUEVO FORMAPAGO ---#
@app.route('/formapago/agregar',methods=['POST'])    
def formapago_agregar():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            nombre = request.form['nombre']
            dias = request.form['dias']
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM formas_pago WHERE dias = %s AND nombre = %s ",(dias,nombre))            
            formapago = cursor.fetchone()
            if formapago is not None:           
                flash("Forma de Pago ya existe")
                redirect(url_for('formaspago'))                
            else:
                cursor.execute("""INSERT INTO formas_pago(nombre,dias, reg_ing)""" 
	            + """VALUES (%s,%s, NOW())""",(nombre,dias))
                conn.commit()
                flash("Registro Guardado con Exito") 
            return redirect(url_for('formaspago'))

#--- MODIFICAR FORMAPAGO ---#
@app.route('/formapago/editar/<int:id>',methods=['POST','GET'])
def formapago_editar(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        cursor = conn.cursor()
        if request.method == 'POST':
            nombre = request.form['nombre']
            dias = request.form['dias']            
            cursor.execute("""	UPDATE formas_pago SET nombre = %s,dias = %s,reg_mod=NOW()
	        WHERE id = %s """,(nombre,dias,id))
            conn.commit()
            flash("Registro Actualiazado con Exito")
            return redirect(url_for('formaspago'))
        else:
            cursor.execute("SELECT id, nombre,dias FROM formas_pago WHERE id = %s ;",(id))
            formapago = cursor.fetchone()
            if formapago is not None:           
                return render_template('formaspago/edi_formapago.html',form=formapago)               
            else:
                flash("Forma de Pago no existe")
                return redirect(url_for('formaspago'))

#--- ELIMINAR FORMAPAGO ---#
@app.route('/formapago/eliminar/<int:id>',methods=['POST','GET'])
def formapago_eliminar(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        cursor = conn.cursor()
        if request.method == 'POST':
            cursor.execute("DELETE FROM formas_pago WHERE id = %s ",(id))
            conn.commit()        
            flash("Registro Eliminado con Exito")
            return redirect(url_for('formaspago'))
        else:
            cursor.execute("SELECT id,nombre,dias FROM formas_pago WHERE id = %s ",(id))
            formapago = cursor.fetchone()            
            if formapago is not None:
                return render_template('formaspago/eli_formapago.html',form=formapago)
            else:
                flash("Forma de Pago no existe")
                return redirect(url_for('formaspago'))
###------------------------------------------INI FORMAPAGO -------------------------------------------------###
if __name__ == '__main__':
    app.run(port=3000,debug=True)
