from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, cv2, os

ROOT=os.path.dirname(__file__)
AS=os.path.join(ROOT,'assets')
os.makedirs(AS,exist_ok=True)
W,H=1600,900
font_reg='/usr/share/fonts/opentype/inter/Inter-Regular.otf'
font_med='/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf'
font_bold='/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'

def f(path,size): return ImageFont.truetype(path,size)

def slide_base(title,kicker='FIELD TEST / AUDIENCE VIEW'):
    im=Image.new('RGB',(W,H),(247,246,242)); d=ImageDraw.Draw(im)
    d.text((78,58),kicker,font=f(font_med,20),fill=(61,75,67))
    d.text((78,100),title,font=f(font_bold,58),fill=(20,22,20))
    d.line((78,186,1522,186),fill=(205,205,197),width=2)
    return im,d

def make_slides():
    # slide 1: healthy
    im,d=slide_base('The last row should see the same story')
    d.text((86,238),'Three things must survive the room:',font=f(font_med,31),fill=(28,31,29))
    items=[('01','Main idea','One sentence, no decoding required.'),('02','Evidence','Numbers remain readable from distance.'),('03','Action','The audience knows what to do next.')]
    y=320
    for n,h,b in items:
        d.rounded_rectangle((86,y,1510,y+128),radius=22,outline=(191,193,186),width=2,fill=(252,251,248))
        d.text((112,y+31),n,font=f(font_bold,28),fill=(33,93,66)); d.text((180,y+24),h,font=f(font_bold,31),fill=(24,26,24)); d.text((180,y+69),b,font=f(font_reg,25),fill=(72,76,72))
        y+=150
    d.text((86,807),'BACKROW demo deck · slide 1/3',font=f(font_reg,18),fill=(110,110,105))
    im.save(os.path.join(AS,'slide_1_source.png'))

    # slide 2: mixed sizes, small critical footnote
    im,d=slide_base('A good headline can hide a bad detail')
    d.text((90,244),'Project completion',font=f(font_med,26),fill=(70,73,69))
    d.text((90,282),'84%',font=f(font_bold,118),fill=(20,22,20))
    d.text((90,430),'On track',font=f(font_bold,36),fill=(33,93,66))
    # chart
    x0,y0=640,272
    vals=[0.38,0.55,0.71,0.84]
    labs=['W1','W2','W3','W4']
    for i,v in enumerate(vals):
        x=x0+i*190
        d.rounded_rectangle((x,710-int(v*420),x+105,710),radius=12,fill=(44,76,61))
        d.text((x+24,735),labs[i],font=f(font_med,22),fill=(50,53,50))
        d.text((x+15,680-int(v*420)),f'{int(v*100)}%',font=f(font_bold,22),fill=(28,30,28))
    # deliberately small but important
    d.rounded_rectangle((88,612,540,742),radius=18,fill=(236,232,221))
    d.text((112,635),'Decision condition',font=f(font_bold,22),fill=(49,44,35))
    d.text((112,679),'Launch only if error rate stays below 2.5%.',font=f(font_reg,20),fill=(74,68,56))
    d.text((88,817),'Source note: the 2.5% threshold is decision-critical.',font=f(font_med,18),fill=(95,80,52))
    im.save(os.path.join(AS,'slide_2_source.png'))

    # slide 3: low contrast chart labels
    im,d=slide_base('Projected contrast is not laptop contrast')
    d.text((92,245),'Same slide. Different room.',font=f(font_med,30),fill=(51,54,51))
    # cards
    d.rounded_rectangle((92,318,748,705),radius=24,fill=(232,233,227))
    d.text((126,354),'LAPTOP',font=f(font_bold,24),fill=(49,52,49))
    d.text((126,406),'Looks fine',font=f(font_bold,55),fill=(30,32,30))
    d.text((126,493),'High local contrast',font=f(font_reg,28),fill=(91,94,91))
    d.text((126,539),'Sharp edges',font=f(font_reg,28),fill=(91,94,91))
    d.text((126,585),'Tiny labels feel readable',font=f(font_reg,28),fill=(91,94,91))
    d.rounded_rectangle((782,318,1508,705),radius=24,fill=(224,223,217))
    d.text((818,354),'ROOM',font=f(font_bold,24),fill=(102,103,98))
    # low contrast on purpose
    d.text((818,406),'Labels disappear',font=f(font_bold,50),fill=(70,73,69))
    d.text((818,493),'Ambient light',font=f(font_reg,25),fill=(92,95,91))
    d.text((818,537),'Projector washout',font=f(font_reg,25),fill=(92,95,91))
    d.text((818,581),'Off-axis viewing',font=f(font_reg,25),fill=(92,95,91))
    d.text((92,812),'BACKROW checks the captured audience view, not the source file alone.',font=f(font_med,20),fill=(65,67,64))
    im.save(os.path.join(AS,'slide_3_source.png'))

    # slide 2 fixed: same message, but the decision-critical condition is made materially larger.
    im,d=slide_base('A good headline can hide a bad detail')
    d.text((90,244),'Project completion',font=f(font_med,26),fill=(70,73,69))
    d.text((90,282),'84%',font=f(font_bold,118),fill=(20,22,20))
    d.text((90,430),'On track',font=f(font_bold,36),fill=(33,93,66))
    x0,y0=640,272
    vals=[0.38,0.55,0.71,0.84];labs=['W1','W2','W3','W4']
    for i,v in enumerate(vals):
        x=x0+i*190
        d.rounded_rectangle((x,710-int(v*420),x+105,710),radius=12,fill=(44,76,61))
        d.text((x+24,735),labs[i],font=f(font_med,22),fill=(50,53,50))
        d.text((x+15,680-int(v*420)),f'{int(v*100)}%',font=f(font_bold,22),fill=(28,30,28))
    d.rounded_rectangle((80,545,610,745),radius=22,fill=(224,236,226),outline=(90,125,98),width=3)
    d.text((110,575),'DECISION CONDITION',font=f(font_bold,23),fill=(35,82,55))
    d.text((110,625),'Error rate must stay',font=f(font_med,35),fill=(28,34,29))
    d.text((110,670),'BELOW 2.5%',font=f(font_bold,50),fill=(20,49,31))
    im.save(os.path.join(AS,'slide_2_source_fixed.png'))

    # PDF generated with Pillow so demo-asset generation has no AGPL dependency.
    pdf_images=[Image.open(os.path.join(AS,f'slide_{i}_source.png')).convert('RGB') for i in range(1,4)]
    try:
        pdf_images[0].save(os.path.join(AS,'demo_deck.pdf'),save_all=True,append_images=pdf_images[1:],resolution=100.0)
    finally:
        for img in pdf_images: img.close()


def project_view(src_path,out_path,case):
    src=cv2.imread(src_path)
    h,w=src.shape[:2]
    canvas=np.full((1120,1800,3),35,np.uint8)
    if case=='good':
        dst=np.float32([[130,120],[1665,80],[1710,960],[90,990]])
        blur=0.55; brightness=0.94
    elif case=='tiny':
        dst=np.float32([[245,155],[1570,120],[1640,925],[190,955]])
        blur=1.55; brightness=0.78
    else:
        dst=np.float32([[160,135],[1650,110],[1710,970],[105,980]])
        blur=1.15; brightness=0.72
    sp=np.float32([[0,0],[w-1,0],[w-1,h-1],[0,h-1]])
    M=cv2.getPerspectiveTransform(sp,dst)
    warped=cv2.warpPerspective(src,M,(canvas.shape[1],canvas.shape[0]))
    mask=cv2.warpPerspective(np.full((h,w),255,np.uint8),M,(canvas.shape[1],canvas.shape[0]))
    canvas[mask>0]=warped[mask>0]
    canvas=(canvas.astype(np.float32)*brightness).clip(0,255).astype(np.uint8)
    if blur>0: canvas=cv2.GaussianBlur(canvas,(0,0),blur)
    # ambient gradient
    yy,xx=np.mgrid[0:canvas.shape[0],0:canvas.shape[1]]
    amb=(18*(xx/canvas.shape[1]) + 8*(yy/canvas.shape[0]))[...,None]
    canvas=np.clip(canvas.astype(np.float32)+amb,0,255).astype(np.uint8)
    if case=='glare':
        overlay=canvas.copy()
        cv2.ellipse(overlay,(1350,590),(430,310),-18,0,360,(250,250,245),-1)
        canvas=cv2.addWeighted(overlay,0.72,canvas,0.28,0)
        # projector washout on the audience-right half
        roi=canvas[350:850,900:1700].astype(np.float32)
        canvas[350:850,900:1700]=np.clip(roi*0.42+255*0.58,0,255).astype(np.uint8)
    if case=='tiny':
        # slight foreground obstruction over bottom-left threshold card edge
        cv2.rectangle(canvas,(180,845),(570,1030),(38,38,38),-1)
    # vignette edges
    cx,cy=canvas.shape[1]/2,canvas.shape[0]/2
    r=((xx-cx)**2/(cx**2)+(yy-cy)**2/(cy**2))
    vig=np.clip(1-0.12*r,0.78,1)[...,None]
    canvas=np.clip(canvas.astype(np.float32)*vig,0,255).astype(np.uint8)
    cv2.imwrite(out_path,canvas,[cv2.IMWRITE_PNG_COMPRESSION,4])

if __name__=='__main__':
    make_slides()
    project_view(os.path.join(AS,'slide_1_source.png'),os.path.join(AS,'slide_1_view_good.png'),'good')
    project_view(os.path.join(AS,'slide_2_source.png'),os.path.join(AS,'slide_2_view_risk.png'),'tiny')
    project_view(os.path.join(AS,'slide_3_source.png'),os.path.join(AS,'slide_3_view_glare.png'),'glare')
    project_view(os.path.join(AS,'slide_2_source_fixed.png'),os.path.join(AS,'slide_2_view_fixed.png'),'tiny')
    print('generated demo assets')
