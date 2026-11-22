"""A deterministic, standard-library newspaper front page."""
import os, struct, zlib

W = H = 1024
PAPER, INK, RED, FADE, LINE = (247,244,235), (21,24,25), (150,37,35), (100,98,91), (190,186,174)

# A compact, deliberately embedded 5 by 7 newsroom typeface.
ROWS = {
'A':[14,17,17,31,17,17,17],'B':[30,17,17,30,17,17,30],'C':[15,16,16,16,16,16,15],
'D':[30,17,17,17,17,17,30],'E':[31,16,16,30,16,16,31],'F':[31,16,16,30,16,16,16],
'G':[15,16,16,23,17,17,15],'H':[17,17,17,31,17,17,17],'I':[31,4,4,4,4,4,31],
'J':[7,2,2,2,2,18,12],'K':[17,18,20,24,20,18,17],'L':[16,16,16,16,16,16,31],
'M':[17,27,21,21,17,17,17],'N':[17,25,21,19,17,17,17],'O':[14,17,17,17,17,17,14],
'P':[30,17,17,30,16,16,16],'Q':[14,17,17,17,21,18,13],'R':[30,17,17,30,20,18,17],
'S':[15,16,16,14,1,1,30],'T':[31,4,4,4,4,4,4],'U':[17,17,17,17,17,17,14],
'V':[17,17,17,17,17,10,4],'W':[17,17,17,21,21,21,10],'X':[17,17,10,4,10,17,17],
'Y':[17,17,10,4,4,4,4],'Z':[31,1,2,4,8,16,31],
'0':[14,17,19,21,25,17,14],'1':[4,12,4,4,4,4,14],'2':[14,17,1,2,4,8,31],
'3':[30,1,1,14,1,1,30],'4':[2,6,10,18,31,2,2],'5':[31,16,16,30,1,1,30],
'6':[14,16,16,30,17,17,14],'7':[31,1,2,4,8,8,8],'8':[14,17,17,14,17,17,14],
'9':[14,17,17,15,1,1,14],'?':[14,17,1,2,4,0,4],'!':[4,4,4,4,4,0,4],
'.':[0,0,0,0,0,0,4],',':[0,0,0,0,0,4,8],"'":[4,4,0,0,0,0,0],
'-':[0,0,0,31,0,0,0],':':[0,4,0,0,4,0,0],';':[0,4,0,0,4,8,0],
'(':[2,4,8,8,8,4,2],')':[8,4,2,2,2,4,8],'/':[1,2,2,4,8,8,16],
'%':[17,2,4,8,16,18,1],'+':[0,4,4,31,4,4,0],'&':[12,18,20,8,21,18,13],
' ': [0,0,0,0,0,0,0], '_':[0,0,0,0,0,0,31]
}
pix = bytearray(PAPER * (W*H))
def rect(x,y,w,h,c):
    x=max(0,x); y=max(0,y); w=min(w,W-x); h=min(h,H-y)
    for yy in range(y,y+h): pix[(yy*W+x)*3:(yy*W+x+w)*3] = bytes(c)*w
def rule(x1,y,x2,c=LINE): rect(x1,y,x2-x1+1,1,c)
def text(x,y,s,scale=1,c=INK,spacing=1):
    xx=x
    for ch in s.upper():
        g=ROWS.get(ch, ROWS['?'])
        for ry,bits in enumerate(g):
            for rx in range(5):
                if bits & (16>>rx): rect(xx+rx*scale,y+ry*scale,scale,scale,c)
        xx += 5*scale+spacing
    return xx
def tw(s, scale=1, spacing=1): return len(s)*(5*scale+spacing)-spacing
def wrap(s, maxw, scale=1, spacing=1):
    out=[]; line=''
    for word in s.split(' '):
        new=word if not line else line+' '+word
        if line and tw(new,scale,spacing)>maxw: out.append(line); line=word
        else: line=new
    if line: out.append(line)
    return out
def lines(x,y,items,maxw,scale=1,c=INK,leading=None,limit=None):
    yy=y; leading=leading or 8*scale
    for s in wrap(items,maxw,scale):
        if limit is not None and yy+7*scale>limit: break
        text(x,yy,s,scale,c); yy+=leading
    return yy

main = ("IRAN STRIKES BAHRAIN SITE AS TANKERS HIT IN HORMUZ", "Bahrain said two people were injured in Saturday's strike on a civilian industrial site as it intercepted fresh Iranian attacks on Sunday; two tankers were hit in Hormuz, and Tehran readied 14 tankers to defy the US blockade.", "MIDDLE EAST / CONFLICT")
top2 = [
("COP31 CLIMATE TALKS COLLAPSE IN CHAOS OVER FOSSIL FUELS", "The Antalya summit ended in failure as nearly 200 nations rejected a final text that never mentioned fossil fuels; the EU and island states refused to endorse it after the longest COP on record.", "CLIMATE"),
("UKRAINE STRAINS RUSSIAN LOGISTICS WITH CRIMEAN BRIDGE STRIKES", "Kyiv's strikes squeezed Russian supply lines, and a Russian cargo ship burned in the Baltic after a drone strike.", "EUROPE / CONFLICT")]
briefs = [
("NATO VOWS TO DEFEND 'EVERY INCH' OF POLAND","The pledge followed a Russian airspace violation over Polish territory.","EUROPE / POLITICS"),
("MEXICO CAPTURES CARTEL LORD 'EL CHAPO ISIDRO'","The Sinaloa boss was seized in a string of arrests; violence after the capture left 11 dead in Sinaloa.","LATIN AMERICA / CRIME"),
("HACKERS BREACH FBI AND US AGRICULTURE DEPARTMENT","Trump confirmed the FBI crime database was hacked as the Agriculture Department breach was reported.","NORTH AMERICA / TECH"),
("FRENCH PROTESTERS RALLY FOR SIXTH WEEKEND OVER LIVING COSTS","Marches across France stayed largely peaceful; thousands also marched in Lisbon.","EUROPE / SOCIETY"),
("NIGERIA BOAT CAPSIZES KILLING AT LEAST 24","The boat was carrying people to a funeral when it overturned.","AFRICA / DISASTER"),
("FIRE AT JAKARTA FACTORY KILLS THREE, 36 MISSING","A blaze at a confectionery factory near Jakarta left three dead as the search continued.","ASIA / DISASTER"),
("TRUMP VOWS TO WORK WITH DEMOCRATS ON CREDIT CARD CAP","He promised to pursue a 10% cap on credit card interest rates.","NORTH AMERICA / POLITICS"),
("NVIDIA FACES ACCOUNTING PROBE REPORT AMID TURMOIL","The chip giant faced reports of a US accounting probe as leadership and China spy claims swirled.","NORTH AMERICA / BUSINESS"),
("IRAN SAYS HORMUZ COULD REOPEN ON 'REASONABLE' TERMS","Tehran signalled the strait could reopen if Washington accepted its terms.","MIDDLE EAST / DIPLOMACY"),
("QATAR AND GERMANY URGE IRAN ON HOUTHIS AND NUCLEAR TALKS","Both called on Tehran to end support for the Houthis and increase nuclear transparency.","MIDDLE EAST / DIPLOMACY"),
("IRAN UNVEILS NEW UNDERGROUND MISSILE FACILITY","The unveiling came amid the escalation across the Gulf.","MIDDLE EAST / MILITARY"),
("IRAN WAR HAS COST US OVER $48BN, PENTAGON SAYS","The figure emerged as the conflict widened across the Gulf.","NORTH AMERICA / MILITARY"),
("SOUTH KOREA EDUCATION CHIEF QUITS OVER AI CHEATING SCANDAL","The education chief resigned amid an AI cheating scandal.","ASIA / POLITICS"),
("AUSTRALIA CRITICISES US BUDGET OFFICE OVER AUKUS","Canberra pushed back at the Congressional Budget Office's comments on the defence pact.","ASIA PACIFIC / POLITICS"),
("CHINA OPPOSES US TELECOM BAN, WARNS OF RETALIATION","Beijing objected to the US move on phone-number access for Chinese telecom firms.","ASIA / TRADE"),
("XI STRENGTHENS HIS HAND AS TRUMP BASKS IN SUMMIT POMP","The summit spotlight masked Beijing's growing leverage, analysts said.","ASIA / ANALYSIS"),
("MIDTERM DEFEAT CORNERS VANCE AS 2028 FIELD WIDENS","The Republicans' midterm defeat squeezed the vice president's path to 2028.","NORTH AMERICA / POLITICS"),
("SENATE DEMOCRATS FACE EARLY LEADERSHIP TEST","A leadership vote tested the new Senate majority's promise of change.","NORTH AMERICA / POLITICS"),
("COUNTRIES OPEN PATH TO ACCORD ON 'KILLER ROBOTS'","Talks advanced toward an agreement on autonomous weapons.","WORLD / TECH"),
("IRAQI FORCES ENTER PRO-IRAN MILITIA STRONGHOLD","Iraqi troops moved into the militia's base area.","MIDDLE EAST / CONFLICT"),
("PENTAGON MOVES TO RESTRICT DEFENCE TIES WITH CANADA","Washington weighed limits even as Canada said military ties were unchanged.","NORTH AMERICA / MILITARY"),
("AMERICA-BOUND MIGRANT CARAVAN REACHES MEXICO","The caravan crossed into Mexico on its way north.","LATIN AMERICA / MIGRATION"),
("UK MAN SWIMS STRAIT OF HORMUZ FOR ENVIRONMENT","He swam the strait to highlight environmental damage from the conflict.","WORLD / ENVIRONMENT"),
("UN WARNS YOUTH FACE ADULTHOOD IN ECONOMIC INSECURITY","The UN flagged job and housing insecurity for young people worldwide.","WORLD / SOCIETY"),
("VERSTAPPEN WINS LAS VEGAS GRAND PRIX THRILLER","The Red Bull driver held off McLaren pair Norris and Piastri in a frenetic night race on the Las Vegas Strip.","SPORT / FORMULA 1"),
("FRENCH COLT ELDENARI LANDS MILE CHAMPIONSHIP IN KYOTO","A first foreign-trained winner of the Kyoto race, beating Embroidery and Star Anis.","SPORT / HORSE RACING"),
("MAO SHIMADA WINS FINLANDIA TROPHY, BOOKS FINAL SPOT","The Japanese skater won in Finland to book her place in the Grand Prix Final.","SPORT / FIGURE SKATING"),
("SCOTLAND OVERPOWER JAPAN IN NATIONS CHAMPIONSHIP","Scotland beat Japan in the rugby clash.","SPORT / RUGBY"),
("ALL BLACKS COACH RENNIE ON HOT SEAT AFTER ENGLAND LOSS","A poor showing against England piled pressure on New Zealand's coach.","SPORT / RUGBY"),
("MANCHESTER CITY SLUMP CONTINUES","Frustration mounted as City's poor run stretched on.","SPORT / SOCCER"),
("PRINCESS AIKO RETURNS FROM SINGAPORE VISIT","Japan's princess completed her visit to Singapore.","JAPAN"),
("BIG-DEPOSIT ACCOUNTS SURGE, BOJ SAYS","Bank accounts holding over 100 million yen surged, the Bank of Japan said.","JAPAN / ECONOMY"),
("LDP FIGURE HINTS AT REPLACING EDUCATION MINISTER","A senior LDP executive suggested swapping out the scandal-hit minister.","JAPAN / POLITICS"),
("JAPAN EYES ORGANIC CHEMICALS FOR CRITICAL PRODUCTS LIST","Tokyo weighed adding organic chemicals to its strategic products list.","JAPAN / POLICY"),
("NAGANO CELERY FARMERS RUN OUT OF ALTITUDE","Warming pushed the key celery crop beyond its highland refuges.","JAPAN / CLIMATE"),
("CHRISTIANS REPORT RISING ATTACKS IN WEST BENGAL","Community leaders complained of more attacks in the Indian state.","ASIA / SOCIETY")]

def ship(x,y):
    rect(x,y+7,43,3,INK); rect(x+6,y+4,25,3,INK); rect(x+13,y,9,4,INK); rect(x+34,y+3,3,4,RED)
def map_panel():
    x,y=742,102; rect(x,y,252,126,(232,228,216)); rule(x,y,x+251,RED); rule(x,y+125,x+251,RED)
    # stylised Strait / Arabian coastline, sea lanes, two tankers
    rect(x+18,y+24,71,9,INK); rect(x+42,y+33,24,28,INK); rect(x+167,y+19,56,10,INK); rect(x+184,y+29,31,31,INK)
    for i in range(5): rule(x+83+i*17,y+76-i*5,x+100+i*17,FADE)
    text(x+13,y+98,"HORMUZ",2,RED); ship(x+92,y+48); ship(x+151,y+73)
def world_map(x,y):
    # recognisable dot-matrix continents, red markers
    dots=[(8,7),(14,5),(20,8),(25,12),(22,18),(17,20),(46,7),(52,5),(58,8),(62,12),(58,18),(52,21),(76,7),(84,5),(94,8),(101,13),(96,18),(88,21),(103,26),(108,31),(15,29),(20,34),(24,40),(27,46)]
    for a,b in dots: rect(x+a*1,y+b//2,3,3,FADE)
    for a,b in [(58,12),(64,15),(82,13),(91,11),(104,29),(21,35),(49,9)]: rect(x+a,y+b//2,4,4,RED)
def render():
    rule(18,14,1005); text(72,27,"THE WORLD IN ONE PAGE",5,INK); text(271,69,"SUNDAY, NOVEMBER 22, 2026",3,RED); rule(18,94,1005)
    text(28,108,"LEAD",1,RED)
    # The lead's following baselines are derived from actual wrapped-line count:
    # this keeps the long headline and summary in separate, bounded bands.
    lead_end=lines(28,124,main[0],690,3,INK,25)
    summary_end=lines(28,lead_end+3,main[1],690,2,INK,15)
    text(28,summary_end+2,main[2],1,RED); map_panel(); rule(18,248,1005)
    for i,(hh,ss,tag) in enumerate(top2):
        x=28+i*494; text(x,260,"TOP STORY",1,RED); lines(x,275,hh,466,2,INK,16); lines(x,323,ss,466,1,INK,8); text(x,350,tag,1,RED)
    # WORLD WATCH is its own full-width band: its dot field is deliberately kept
    # out of the brief columns, with rules defining both of its edges.
    rule(18,369,1005)
    text(28,397,"WORLD WATCH",1,RED)
    world_map(456,391)
    rule(18,440,1005)
    # 12 compact, measured brief cells per column.  At this scale each cell has
    # a tag, up to two headline lines, and a separately bounded summary line.
    top=452; cell=43; colw=315
    for col in range(3):
        x=28+col*332
        if col: rect(x-16,top,1,516,LINE)
        for row in range(12):
            hh,ss,tag=briefs[col*12+row]; y=top+row*cell
            text(x,y,tag,1,RED)
            end=lines(x,y+9,hh,colw,1,INK,8, y+25)
            lines(x,end+1,ss,colw,1,FADE,8,y+41)
            rule(x,y+42,x+colw-1,(218,214,204))
    rule(18,984,1005); text(188,996,"22 NOVEMBER 2026 - THE DAY'S WORLD NEWS",2,INK)
def png(path):
    raw=b''.join(b'\0'+bytes(pix[y*W*3:(y+1)*W*3]) for y in range(H))
    def chunk(t,d): return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    data=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')
    os.makedirs(os.path.dirname(path) or '.',exist_ok=True)
    with open(path,'wb') as f: f.write(data)
if __name__ == '__main__':
    render(); png(os.environ.get('OUTPUT_PATH','/output/entry.png'))
