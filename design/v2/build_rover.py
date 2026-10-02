"""Photo-referenced Rover model. Run with Blender 4.5: blender -b --python build_rover.py.
All construction measurements below are in millimetres; the saved scene uses metres.
The chassis dimensions are estimates, not a manufacturing drawing.
"""
import bpy, math, random, json, sys, os
from pathlib import Path
from mathutils import Vector, Matrix

OUT = Path(__file__).resolve().parent
REFERENCE_DIR = Path(os.environ.get('ROVER_REFERENCE_DIR', str(OUT / 'private-reference-photos')))
M = 0.001
random.seed(17)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name != 'Collection': bpy.data.collections.remove(c)
base = bpy.data.collections.get('Collection')
base.name = 'ROVER | photo-referenced model'
COLS = {}
for name in ['01 Chassis','02 Wheels','03 Raspberry Pi','04 Webcam','05 Cables','06 Markings','07 Studio','08 References']:
    c = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c); COLS[name] = c
root = bpy.data.objects.new('ROVER | move the complete model', None)
base.objects.link(root); root.empty_display_size = .025
root['description'] = 'Reconstruction from IMG_8361–IMG_8364. Estimated scale; visible hardware details modelled, hidden underside simplified.'
root['front_direction'] = '-Y'; root['units'] = 'metres'
root['scale_reference'] = 'Raspberry Pi board nominal 85 × 56 mm; other dimensions estimated from photographs.'
current = '01 Chassis'

def own(o, name, mat=None, parent=True):
    o.name = name
    for c in list(o.users_collection): c.objects.unlink(o)
    COLS[current].objects.link(o)
    if mat: o.data.materials.append(mat)
    if parent: o.parent = root
    return o

def material(name, color, rough=.4, metal=0, noise=0):
    a = bpy.data.materials.new(name); a.diffuse_color = (*color,1); a.use_nodes=True
    nt=a.node_tree; p=nt.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    if noise:
        n=nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value=600
        b=nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value=noise; b.inputs['Distance'].default_value=.0001
        nt.links.new(n.outputs['Fac'],b.inputs['Height']); nt.links.new(b.outputs['Normal'],p.inputs['Normal'])
    return a

paint=material('Chassis | satin black powder coat',(.018,.023,.025),.37,.55,.2)
edge=material('Cut metal edges',(.055,.063,.067),.29,.72)
rubber=material('Tires | charcoal rubber',(.022,.027,.030),.81,0,.18)
treadmat=material('Tread blocks | textured rubber',(.028,.033,.036),.78,0,.22)
gloss=material('Wheel rims | gloss black',(.006,.009,.012),.13,.28)
plastic=material('Webcam | moulded graphite',(.031,.040,.046),.43,0,.08)
dark=material('Recesses | near black',(.003,.005,.006),.6)
silver=material('Brushed metal',(.48,.55,.57),.26,.85)
gold=material('Brass contacts',(.58,.39,.075),.32,.72)
pcb=material('PCB | green solder mask',(.035,.23,.125),.42,.15)
trace=material('PCB traces under solder mask',(.051,.28,.15),.5,.18)
silk=material('PCB silkscreen',(.59,.72,.61),.62)
solder=material('Solder pads',(.57,.64,.61),.27,.78)
cablemat=material('USB cable | black PVC',(.008,.012,.017),.39)
red=material('Cable tie | red fabric',(.48,.009,.035),.9,0,.5)
yellow=material('Warning label | warm yellow',(.97,.62,.018),.46)
white=material('White print',(.86,.90,.9),.46)
lensmat=material('Lens | blue optical glass',(.013,.04,.057),.10,.5)

def bevel(o, amount=.6, segments=3):
    b=o.modifiers.new('Soft manufactured edges','BEVEL'); b.width=amount*M; b.segments=segments
    b.limit_method='ANGLE'
    return o

def smooth(o):
    for p in o.data.polygons: p.use_smooth=True
    return o

def box(name, loc, dims, mat, bev=.5, rot=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=Vector(loc)*M)
    o=own(bpy.context.object,name,mat); o.dimensions=Vector(dims)*M
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bev: bevel(o,bev,4)
    if rot: o.rotation_euler=rot
    return o

def cylinder(name, loc, radius, depth, mat, axis=(0,0,1), vertices=48, bev=.25):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius*M,depth=depth*M,location=Vector(loc)*M)
    o=own(bpy.context.object,name,mat)
    o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler()
    if bev: bevel(o,bev,2)
    smooth(o)
    return o

def mesh(name, verts, faces, mat, bev=0):
    d=bpy.data.meshes.new(name); d.from_pydata([tuple(Vector(v)*M) for v in verts],[],faces); d.update()
    o=bpy.data.objects.new(name,d); COLS[current].objects.link(o); o.parent=root
    if mat:d.materials.append(mat)
    if bev:bevel(o,bev)
    return o

def panel(name, poly, z, thickness, mat, bev=.4):
    n=len(poly); vs=[(x,y,z+dz) for dz in [-thickness/2,thickness/2] for x,y in poly]
    fs=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,vs,fs,mat,bev)

def ring(name, loc, outer, inner, thick, mat, axis=(0,0,1), segments=64):
    axis=Vector(axis).normalized(); q=axis.to_track_quat('Z','Y'); vs=[]
    for z,r in [(-thick/2,outer),(thick/2,outer),(-thick/2,inner),(thick/2,inner)]:
        for i in range(segments):
            a=i*math.tau/segments; v=q@Vector((r*math.cos(a),r*math.sin(a),z))+Vector(loc); vs.append(v)
    fs=[]
    for a,b in [(0,1),(2,0),(1,3),(3,2)]:
        for i in range(segments):j=(i+1)%segments;fs.append((a*segments+i,a*segments+j,b*segments+j,b*segments+i))
    return smooth(mesh(name,vs,fs,mat,.1))

def curve(name, points, radius, mat, cyclic=False, poly=False):
    d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.resolution_u=16;d.bevel_depth=radius*M;d.bevel_resolution=3
    s=d.splines.new('POLY' if poly else 'BEZIER')
    if poly:
        s.points.add(len(points)-1)
        for p,v in zip(s.points,points):p.co=(*[x*M for x in v],1)
    else:
        s.bezier_points.add(len(points)-1)
        for p,v in zip(s.bezier_points,points):p.co=Vector(v)*M;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    s.use_cyclic_u=cyclic
    o=bpy.data.objects.new(name,d);COLS[current].objects.link(o);o.parent=root;d.materials.append(mat)
    return o

def text(name, content, loc, size, mat, rot=(0,0,0), align='LEFT'):
    d=bpy.data.curves.new(name,'FONT');d.body=content;d.size=size*M;d.space_line=1.0;d.extrude=.015*M;d.resolution_u=3;d.align_x=align
    o=bpy.data.objects.new(name,d);COLS[current].objects.link(o);o.parent=root;o.location=Vector(loc)*M;o.rotation_euler=rot;d.materials.append(mat)
    return o

def bolt(name, loc, size=2, axis=(0,0,1)):
    cylinder(name+' socket head',loc,size,1.5,paint,axis,32,.2)
    d=Vector(axis).normalized()*.78+Vector(loc)
    cylinder(name+' hex recess',d,size*.49,.06,dark,axis,6,0)

def cut(target,cutter):
    bpy.context.view_layer.objects.active=target
    # Apply the cut before the bevel modifier.
    b=target.modifiers.new('Plate opening','BOOLEAN');b.operation='DIFFERENCE';b.object=cutter
    bpy.ops.object.modifier_move_up(modifier=b.name)
    bpy.ops.object.modifier_apply(modifier=b.name)
    bpy.data.objects.remove(cutter,do_unlink=True)

# --- Folded and bolted sheet-metal chassis ---
outline=[(-82,-106),(82,-106),(96,-91),(96,92),(83,106),(-83,106),(-96,92),(-96,-91)]
deck=panel('Deck | bevelled 2.4 mm plate',outline,100,2.4,paint,.65)
cut(deck,box('Cutter | electronics opening',(14,8,100),(78,105,12),None,0))
for x in [-69,69]:
    for y in [-68,67]:
        cut(deck,cylinder('Cutter | fastener hole',(x,y,100),1.7,10,None,bev=0))
box('Lower chassis enclosure',(0,1,73),(101,166,43),paint,4)
panel('Underside service panel',[(-59,-76),(59,-76),(59,77),(-59,77)],51.2,1.5,paint,.7)
for y in [-81,80]:box('Crossmember',(0,y,64),(154,9,13),paint,1)
for x in [-48,48]:box('Longitudinal frame rail',(x,0,70),(6,160,29),paint,.6)
for x in [-70,70]:
    for y in [-70,70]:bolt('Deck fastener',(x,y,102),2.6)
for x in [-53,53]:
    for y in [-67,68]:bolt('Underside fastener',(x,y,50.2),1.9,(0,0,-1))
# Folded leading and trailing aprons.
front=mesh('Front folded lip',[(-82,-106,100),(82,-106,100),(91,-99,91),(76,-108,86),(-76,-108,86),(-91,-99,91)],[(0,1,2,3,4,5)],paint)
front.modifiers.new('Sheet thickness','SOLIDIFY').thickness=1.8*M;bevel(front,.65)
back=mesh('Rear folded panel',[(-83,106,100),(83,106,100),(80,109,80),(53,109,70),(-53,109,70),(-80,109,80)],[(0,1,2,3,4,5)],paint)
back.modifiers.new('Sheet thickness','SOLIDIFY').thickness=1.8*M;bevel(back,.65)
for y in [-61,61]:cylinder('Wheel axle',(0,y,49.8),3.8,178,edge,(1,0,0))
for s in [-1,1]:
    side=mesh('Side warning plate '+str(s),[(s*96,-33,100),(s*96,33,100),(s*98,19,76),(s*98,-19,76)],[(0,1,2,3)],paint)
    side.modifiers.new('Plate thickness','SOLIDIFY').thickness=1.8*M;bevel(side,.65)
    for y in [-87,87]:box('Wheel guard end',(s*92,y,95),(9,17,11),paint,1.7)

# --- Wheels: exact manufacturer tread and moulded hub mesh ---
current='02 Wheels'
wheel_data=json.loads((OUT/'assets/wave-rover-wheel.json').read_text())
WHEEL_SCALE=49.8/40.586

def wheel(s,y,label):
    pivot=bpy.data.objects.new(label+' | wheel pivot, rotate local X',None)
    COLS[current].objects.link(pivot);pivot.parent=root
    pivot.location=Vector((s*78,y,49.8))*M;pivot.empty_display_size=.02
    bpy.context.view_layer.update()
    for key,mat in [('tire',rubber),('hub',gloss)]:
        source=wheel_data[key]
        vertices=[(s*v[0]*WHEEL_SCALE,v[1]*WHEEL_SCALE,v[2]*WHEEL_SCALE) for v in source['vertices']]
        faces=[list(reversed(f)) if s<0 else f for f in source['faces']]
        obj=mesh(label+' | WAVE ROVER '+key,vertices,faces,mat)
        obj.parent=pivot;obj.location=(0,0,0)
        for f in obj.data.polygons:f.use_smooth=True
        if hasattr(obj.data,'set_sharp_from_angle'):obj.data.set_sharp_from_angle(angle=math.radians(32))
        obj['geometry_source']=wheel_data['source']
    pivot['wheel_radius_mm']=49.8
    pivot['reference_nominal_diameter_mm']=80
    pivot['reference_nominal_width_mm']=42.5
    pivot['reference_scale_in_scene']=WHEEL_SCALE
for s,side in [(-1,'Left'),(1,'Right')]:
    for y,end in [(-61,'front'),(61,'rear')]:wheel(s,y,side+' '+end)

# --- Exposed underside of the Raspberry Pi board ---
current='03 Raspberry Pi'
BX=14;BY=8;BZ=114
board=box('Raspberry Pi 4 | 85 × 56 mm board, underside up',(BX,BY,BZ),(56,85,1.6),pcb,1.4)
for x in [-24.5,24.5]:
    for y in [-38.5,32.5]:
        cut(board,cylinder('PCB mounting hole',(BX+x,BY+y,BZ),1.35,7,None,bev=0))
        ring('Plated mounting hole',(BX+x,BY+y,BZ+.86),2.55,1.36,.06,gold)
        cylinder('Board nylon standoff',(BX+x,BY+y,107),2.55,11,paint,vertices=12)
# Under-board port housings, visibly upside-down like the reference.
for x in [-18,0]:
    box('Dual USB housing',(BX+x,BY+35,107),(14.5,17,12),silver,.45)
    for z in [104,109]:box('USB black aperture',(BX+x,BY+43.7,z),(11.8,.4,3.5),dark,.2)
box('Ethernet housing',(BX+18,BY+32,105.5),(16,21,14),silver,.5)
box('Ethernet port opening',(BX+18,BY+42.7,105),(12.5,.35,8.2),dark,.35)
for y in [-23,-5]:
    box('Micro HDMI shell',(BX+28.6,BY+y,110),(4.6,7.5,3.5),silver,.5)
    box('Micro HDMI aperture',(BX+31,BY+y,110),(.2,5.3,1.9),dark,.2)
box('USB-C power shell',(BX+28.7,BY-33,110),(4.5,8.4,3.4),silver,.8)
box('USB-C power aperture',(BX+31.1,BY-33,110),(.2,6.1,1.7),dark,.55)
cylinder('AV jack',(BX+28.9,BY+13,107),3,5,plastic,(1,0,0))
cylinder('AV jack aperture',(BX+31.6,BY+13,107),1.6,.1,dark,(1,0,0),bev=0)
box('GPIO header underneath',(BX-23,BY-1,109),(5.3,52,8),dark,.35)
# Small solder pads, vias and tracks as editable geometry.
for i in range(20):
    for x in [-24.4,-21.9]:cylinder('GPIO solder pad',(BX+x,BY-27+i*2.54,BZ+.91),.72,.12,solder,vertices=12,bev=0)
for i in range(84):
    x=random.uniform(-21,23);y=random.uniform(-34,36)
    if abs(x)<9 and y<-21:continue
    if i%3==0:
        curve('Fine masked PCB trace',[(BX+x,BY+y,BZ+.83),(BX+x+3,BY+y,BZ+.83),(BX+x+5,BY+y+2,BZ+.83)],.065,trace,poly=True)
    box('SMD resistor body',(BX+x,BY+y,BZ+.98),(.9,1.55,.25),dark,.08)
    for dy in [-.72,.72]:box('SMD solder termination',(BX+x,BY+y+dy,BZ+1.05),(1.05,.42,.24),solder,.06)
for i in range(45):
    x=random.uniform(-22,22);y=random.uniform(-34,36)
    cylinder('PCB test via',(BX+x,BY+y,BZ+.88),.38,.08,gold,vertices=10,bev=0)
# Central underside silkscreen and socket.
text('Pi board silkscreen','Raspberry Pi 4 Model B',(BX-10,BY+21,BZ+.87),2.1,silk,rot=(0,0,math.pi/2))
text('PCB compliance print','CE  UKCA',(BX+6,BY-3,BZ+.88),2.9,silk)
box('MicroSD metal cage',(BX,BY-31,BZ+1.4),(13.5,15,.8),silver,.5)
box('MicroSD red exposed end',(BX,BY-40.2,BZ+1.4),(11.2,5.3,.9),red,.25)
text('MicroSD marking','32',(BX-4,BY-41.7,BZ+1.93),2.3,white)
for x in [-5,5]:
    for y in [-36,-27]:box('SD cage relief',(BX+x,BY+y,BZ+1.85),(.8,2,.06),dark,.06)

# --- C270: thin curved shell, recessed optical well, and folded clip ---
current='04 Webcam'
CX=-33;CY=-100;CZ=116.2
frontmat=material('C270 | dark graphite front shell',(.027,.032,.036),.31,.10)
insertmat=material('C270 | fine textured optical insert',(.011,.014,.016),.58,0,.08)
ledmat=material('C270 | inactive indicator window',(.035,.047,.010),.25)
optical=material('C270 | recessed dark lens',(.003,.008,.009),.12,.2)

def shell(name,cx,cy,cz,width,height,sections,mat,exponent=3.6,N=96):
    vs=[]
    for depth,sx,sz in sections:
        for i in range(N):
            a=math.tau*i/N;co=math.cos(a);si=math.sin(a)
            x=width*.5*math.copysign(abs(co)**(2/exponent),co)*sx
            z=height*.5*math.copysign(abs(si)**(2/exponent),si)*sz
            vs.append((cx+x,cy+depth,cz+z))
    fs=[tuple(range(N)),tuple(reversed(range((len(sections)-1)*N,len(sections)*N)))]
    for j in range(len(sections)-1):
        for i in range(N):
            k=(i+1)%N;fs.append((j*N+i,(j+1)*N+i,(j+1)*N+k,j*N+k))
    obj=mesh(name,vs,fs,mat)
    for f in obj.data.polygons:f.use_smooth=len(f.vertices)==4
    return obj

# The folded universal clip lies on the deck, with no tall vertical pedestal.
foot_poly=[(-20,-22),(20,-22),(23,-19),(23,16),(20,22),(-20,22),(-23,16),(-23,-19)]
foot=panel('C270 | lower folded clip',[(CX+x,-63+y) for x,y in foot_poly],103.1,4.0,plastic,1.5)
box('C270 | rubber foot pad',(CX,-64,100.95),(37,30,.35),dark,.1)
# A curved tapering upper leaf folds over the foot and rises into the camera body.
sections=[(-89,112.6,39),(-83,112.2,43),(-70,109.4,44.5),(-48,108.1,44.5),(-42,106.8,41)]
vs=[];N=40
for y,z,w in sections:
    for i in range(N):
        a=math.tau*i/N;co=math.cos(a);si=math.sin(a)
        vs.append((CX+w*.5*math.copysign(abs(co)**.38,co),y,z+2.6*math.copysign(abs(si)**.38,si)))
fs=[tuple(reversed(range(N))),tuple(range((len(sections)-1)*N,len(sections)*N))]
for j in range(len(sections)-1):
    for i in range(N):k=(i+1)%N;fs.append((j*N+i,j*N+k,(j+1)*N+k,(j+1)*N+i))
leaf=mesh('C270 | curved folding upper clip',vs,fs,plastic)
for f in leaf.data.polygons:f.use_smooth=len(f.vertices)==4
cylinder('C270 | rear clip hinge',(CX,-44,106.5),3.15,44.4,plastic,(1,0,0),64,.25)
for side in [-1,1]:cylinder('C270 | hinge end plug',(CX+side*22.4,-44,106.5),2.55,.5,paint,(1,0,0),48,.2)

head_start=set(bpy.data.objects)
body=shell('C270 | sculpted rear housing',CX,CY,CZ,72.91,31.91,[(-4.7,.996,.99),(-2,1,1),(3,.983,.98),(7,.915,.91),(9.6,.79,.78),(10.7,.54,.54)],plastic)
front=shell('C270 | curved thin faceplate',CX,CY,CZ,72.91,31.91,[(-7.85,.953,.947),(-7.25,.98,.977),(-5.55,.994,.99),(-5.15,.994,.99)],frontmat)
# Recess the complete dark inset into the faceplate.
cut(front,shell('Cutter | optical inset',CX-13.2,CY,CZ+.15,37.1,20.8,[(-10,1,1),(-4,1,1)],None,3.1))
insert=shell('C270 | inset lens and microphone panel',CX-13.2,CY,CZ+.15,36.8,20.5,[(-7.63,1,1),(-6.5,1,1)],insertmat,3.1)
LX=CX-21.2;LZ=CZ+.15
for obj in [body,front,insert]:
    cut(obj,cylinder('Cutter | recessed lens aperture',(LX,CY-6,LZ),6.18,11,None,(0,1,0),96,0))
# The concentric rings step inward, rather than projecting out of the case.
vs=[];fs=[];N=96
profile=[(-7.58,6.16),(-7.15,5.9),(-6.8,5.62),(-6.20,5.60),(-5.8,5.18),(-5.25,5.14),(-4.55,4.60),(-3.45,4.15),(-2.85,3.05)]
for yy,r in profile:
    for i in range(N):
        a=i*math.tau/N;vs.append((LX+r*math.cos(a),CY+yy,LZ+r*math.sin(a)))
for j in range(len(profile)-1):
    for i in range(N):k=(i+1)%N;fs.append((j*N+i,j*N+k,(j+1)*N+k,(j+1)*N+i))
smooth(mesh('C270 | stepped recessed lens well',vs,fs,dark))
cylinder('C270 | deeply inset optical element',(LX,CY-2.69,LZ),3.05,.22,optical,(0,-1,0),96,0)
ring('C270 | inner optical retainer',(LX,CY-2.88,LZ),2.1,1.15,.14,dark,(0,-1,0),64)
cylinder('C270 | lens pupil',(LX,CY-2.99,LZ),1.05,.09,lensmat,(0,-1,0),64,0)
# Nine microphone holes and the slim inactive LED window.
for ix in range(3):
    for iz in range(3):
        cut(insert,cylinder('Cutter | microphone hole',(CX-1.15+ix*1.6,CY-7,LZ-2+iz*2),.33,5,None,(0,1,0),16,0))
curve('C270 | indicator window',[(CX-29.5,CY-7.80,CZ-2.3),(CX-29.8,CY-7.80,CZ),(CX-29.5,CY-7.80,CZ+2.3)],.62,ledmat)
text('C270 | resolution marking','720p',(CX-12.0,CY-7.82,CZ-1.1),1.9,white,(math.pi/2,0,0))
text('C270 | front logo','logi',(CX+15.7,CY-7.97,CZ-2.2),5.2,white,(math.pi/2,0,0))
# Shallow upward pitch, matching the photographed position.
head_parts=set(bpy.data.objects)-head_start
head=bpy.data.objects.new('C270 | camera tilt pivot',None);COLS[current].objects.link(head);head.parent=root;head.location=Vector((CX,CY,CZ))*M;head.empty_display_size=.01
bpy.context.view_layer.update()
for obj in head_parts:
    world=obj.matrix_world.copy();obj.parent=head;obj.matrix_world=world
head.rotation_euler.x=math.radians(-7)
head['reference']='Logitech C270 product reference and owner photographs; shell width 72.91 mm, folded clip depth about 66.6 mm.'

# Front push-button and angled radio antenna.
current='01 Chassis'
ring('Power switch chrome bezel',(18,-84,101.5),7.6,5.8,2.3,silver)
cylinder('Power switch black inner ring',(18,-84,102),5.8,1.4,dark)
cylinder('Power switch brushed button',(18,-84,102.8),5.0,.8,silver,bev=.35)
antenna_base=Vector((48,-84,102)); direction=Vector((.08,-.58,.81)).normalized()
ring('Antenna bulkhead washer',antenna_base,5.6,3.5,1.4,silver)
cylinder('Antenna brass connector',antenna_base+direction*4,3.4,7,gold,direction,bev=.3)
cylinder('Short black antenna',antenna_base+direction*19,4.0,28,cablemat,direction,bev=2.5)

# --- Webcam cable arch, coiled slack, red tie and rear connector ---
current='05 Cables'
curve('Webcam lead | high arch',[(CX,CY+10.5,CZ+4),(-26,-63,158),(-9,-29,174),(6,19,158),(10,55,131)],1.8,cablemat)
for i in range(4):
    x=-11+i*3.9
    curve('Coiled webcam slack '+str(i+1),[(x,54,119),(x+6,70+i,142),(x+11,77,163-i*2),(x+12,71,174-i*1.2),(x+4,59,168-i*2),(x+2,54,141)],1.9,cablemat,True)
curve('Cable to rear USB',[(1,58,121),(22,76,126),(22,102,117),(20,126,94),(14,131,77),(3,110,87),(-4,79,105)],1.8,cablemat)
box('Rear USB plug housing',(BX-18,BY+53,106.7),(12,20,8.6),cablemat,2.4)
cylinder('USB plug strain relief',(BX-18,BY+64,106.7),2.8,8,cablemat,(0,1,0),32,.7)
cylinder('Cable ferrite choke',(20,119,100),4.4,16,cablemat,(0,.7,-.7),32,1.4)
for i in range(3):
    z=139+i*2.1
    curve('Red cable keeper wrap '+str(i),[(-14,59,z),(-5,53,z-4),(12,58,z),(10,66,z+4),(-7,68,z+3)],.9,red,True)
curve('Red cable keeper tail',[(-9,63,140),(-14,59,130),(-10,58,125)],1.2,red)
tag=box('USB cable compliance tag',(18,129,82),(17,.45,19),paint,.4,rot=(.25,-.15,.18))
text('Cable tag print','CE  UKCA\nUSB CAMERA',(10,128.6,84),2,white,(math.pi/2,0,0))

# Side warning stickers; editable geometry and text, no photograph textures.
current='06 Markings'
for s in [-1,1]:
    xx=s*99.3
    pts=[(xx,-28,98.4),(xx,28,98.4),(xx,17,79),(xx,-17,79)]
    decal=mesh('Yellow wheel warning '+str(s),pts,[(0,1,2,3)],yellow)
    # Text XY maps onto side plane with local up along Z.
    horiz=Vector((0,s,0));up=Vector((0,0,1));normal=Vector((s,0,0))
    rot=Matrix((horiz,up,normal)).transposed().to_euler()
    origin=Vector((xx+s*.09,-s*10,93.3))
    text('Wheel warning headline '+str(s),'Do Not Rotate\nWheel by Hand',origin,3.1,dark,rot)
    text('Wheel warning fine print '+str(s),'HIGH GEAR REDUCTION\nAvoid gearbox damage',(xx+s*.1,-s*9,84.2),1.2,dark,rot)
    loc=(xx+s*.1,-s*20,90)
    cylinder('White prohibition badge',loc,6.9,.08,white,(s,0,0),64,0)
    ring('Red prohibition circle',(xx+s*.18,-s*20,90),6.3,5.5,.12,red,(s,0,0),64)
    ring('Wheel symbol',(xx+s*.26,-s*20,90),3.6,2.6,.08,dark,(s,0,0),32)
    curve('Prohibition slash',[(xx+s*.4,-s*24.4,85.6),(xx+s*.4,-s*15.6,94.4)],.55,red,poly=True)

# Scene metadata and source references are stored inside the .blend.
readme=bpy.data.texts.new('READ ME | Rover model')
readme.write('ROVER — PHOTO-REFERENCED RECONSTRUCTION\n\nScale is estimated, as requested. Nominal Pi board 85 × 56 mm.\nFront faces -Y. Scene units are metres; UI measurements display millimetres.\nUse the ROVER root empty to move the complete robot. Four wheel pivots rotate around local X.\nCollections separate chassis, wheels, Pi, webcam, cables, markings, studio and original photo references.\nTire treads and electronics are real geometry. Components are separate editable objects.\nHidden underside and small electronics are simplified; this is a visualization model, not measured CAD.\nSource: IMG_8361, IMG_8362, IMG_8363, IMG_8364 supplied by the owner.\n')
if (OUT/'README.md').exists():
    readme.clear();readme.write((OUT/'README.md').read_text())
current='08 References'
for i,n in enumerate([8361,8362,8363,8364]):
    f=REFERENCE_DIR/f'IMG_{n}.jpg'
    if f.exists():
        im=bpy.data.images.load(str(f));im.pack()
        o=bpy.data.objects.new(f'Reference | IMG_{n}',None);COLS[current].objects.link(o)
        o.empty_display_type='IMAGE';o.data=im;o.empty_display_size=.22;o.location=((i-1.5)*.24,.38,.14);o.rotation_euler=(math.pi/2,0,0);o.hide_render=True
COLS[current].hide_viewport=True;COLS[current].hide_render=True

# --- Studio lighting and four named cameras ---
current='07 Studio'
scene=bpy.context.scene
scene.unit_settings.system='METRIC';scene.unit_settings.length_unit='MILLIMETERS'
floor=material('Studio floor | warm porcelain',(.79,.81,.80),.72)
o=box('Studio ground',(0,0,-3),(2000,2000,5),floor,0);o.parent=None
o.is_shadow_catcher=True
world=bpy.data.worlds.new('Soft neutral studio world');scene.world=world;world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.78,.83,.88,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.22
def aim(o,target):o.rotation_euler=(Vector(target)*M-o.location).to_track_quat('-Z','Y').to_euler()
def light(name,loc,power,size,color,target=(0,0,70)):
    d=bpy.data.lights.new(name,'AREA');d.energy=power*.08;d.shape='DISK';d.size=size*M;d.color=color
    o=bpy.data.objects.new(name,d);COLS[current].objects.link(o);o.location=Vector(loc)*M;aim(o,target)
light('Key | large softbox',(-310,-250,430),27,330,(1,.94,.87))
light('Fill | broad cool softbox',(310,-90,260),18,260,(.84,.91,1))
light('Rim | overhead strip',(80,270,420),35,260,(1,1,1))
light('Front lens reflection',(-10,-400,200),5,140,(1,1,1))
def camera(name,loc,target,ortho):
    d=bpy.data.cameras.new(name);d.type='ORTHO';d.ortho_scale=ortho*M;d.clip_start=.001;d.clip_end=20
    o=bpy.data.objects.new(name,d);COLS[current].objects.link(o);o.location=Vector(loc)*M;aim(o,target);return o
cameras=[camera('Camera | hero',(335,-430,305),(0,0,85),370),camera('Camera | rear',(-320,405,255),(0,0,82),365),camera('Camera | side',(420,0,182),(0,0,86),350),camera('Camera | top',(0,10,570),(0,10,0),370)]
scene.camera=cameras[0]
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.render.resolution_x=1600;scene.render.resolution_y=1280;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
scene.use_nodes=True
nt=scene.node_tree;nt.nodes.clear()
layers=nt.nodes.new('CompositorNodeRLayers')
over=nt.nodes.new('CompositorNodeAlphaOver');over.inputs[1].default_value=(1,1,1,1)
nt.links.new(layers.outputs['Image'],over.inputs[2])
composite=nt.nodes.new('CompositorNodeComposite');nt.links.new(over.outputs['Image'],composite.inputs['Image'])
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
scene.render.image_settings.color_mode='RGBA'
scene.render.fps=30
# Frame a useful shaded viewport when the file opens.
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active;space.clip_start=.001;space.clip_end=20
            space.region_3d.view_distance=.45;space.region_3d.view_location=Vector((0,0,.08))
            space.region_3d.view_rotation=cameras[0].rotation_euler.to_quaternion()
            space.shading.type='MATERIAL';space.overlay.show_floor=False
bpy.ops.object.select_all(action='DESELECT');root.select_set(True);bpy.context.view_layer.objects.active=root
bpy.context.view_layer.update()
model_objs=[o for c in list(COLS.values())[:6] for o in c.objects if o.type in {'MESH','CURVE','FONT'}]
coords=[o.matrix_world@Vector(v) for o in model_objs for v in o.bound_box]
mins=[min(v[k] for v in coords) for k in range(3)];maxs=[max(v[k] for v in coords) for k in range(3)]
stats={'objects':len(model_objs),'bounding_box_mm':[round((maxs[k]-mins[k])*1000,1) for k in range(3)],'scale':'estimated','unit':'metres','blender':bpy.app.version_string}
(OUT/'model-info.json').write_text(json.dumps(stats,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Rover.blend'),compress=True)
print('ROVER_SAVED',json.dumps(stats),flush=True)
# Convert temporary duplicates for GLB while preserving all editable originals in the saved blend.
bpy.ops.object.select_all(action='DESELECT')
for o in model_objs:o.select_set(True)
bpy.context.view_layer.objects.active=model_objs[0]
bpy.ops.object.duplicate()
duplicates=list(bpy.context.selected_objects)
bpy.ops.object.convert(target='MESH')
bpy.ops.export_scene.gltf(filepath=str(OUT/'Rover.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_cameras=False,export_lights=False,export_extras=True)
bpy.ops.object.delete()
print('ROVER_GLB_EXPORTED',flush=True)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if '--no-render' not in args:
    if '--draft' in args:
        scene.render.resolution_percentage=60;scene.cycles.samples=20
    for cam,name in zip(cameras,['Rover-Hero','Rover-Rear','Rover-Side','Rover-Top']):
        if '--draft' in args and name not in ['Rover-Hero','Rover-Side']:continue
        scene.camera=cam;scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
        print('ROVER_RENDERED',name,flush=True)
print('ROVER_COMPLETE',flush=True)
