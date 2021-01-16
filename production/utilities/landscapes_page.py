import os, sys

def readfileNoStrip(filepath):
    with open(filepath) as f:
        lines = f.read().splitlines(True) #keeplinebreaks=True.  Does not strip the lines of \n
    return lines
trackerStr = "&tr=http://tracker.opentrackr.org:1337/announce"
landPage = '/home/bret/servers/repo-skylinesC/skylinesC/ember/app/templates/landscapes.hbs'
dir = '/media/sf_landscapes-zip'
dirlist = os.listdir(dir)
names = []
sizes = []
for item in dirlist:
    if '.torrent' in item:
        name = item.split('.torrent')[0]
        names.append(name)
        sizes.append (os.stat('{}/{}'.format(dir,name)).st_size)
print names

lines = []
lines.append('<BasePage> \n')

lines.append('  <div class="page-header"> \n')
lines.append('    <h1>{{t "landscapes"}}</h1> \n')
lines.append('  </div> \n')
lines.append('  <p> {{t "landscapes-download"}} </p> \n')
# lines.append('  <p> {{t "install"}} <a href="https://www.fosshub.com/qBittorrent.html">  {{"qBittorrent"}}</a> {{t "qbittorent"}} <b> {{t "torrent"}} </b> {{t "torrent-after"}}</p> \n')
lines.append('  <p> {{t "install"}} <a href="https://www.fosshub.com/qBittorrent.html">  {{"qBittorrent"}}</a> {{t "qbittorent"}} <b> {{t "torrent"}} </b> </p> \n')

lines.append('  <p> {{t "extract-with"}}  <a href="https://www.7-zip.org/download.html"> 7-zip </a>  {{t "landscapes-paste"}} </p> \n')
lines.append('  <hr> \n')
lines.append('  <p> <b> {{t "torrent-share"}} </b> {{t "torrent-seed"}} <b> {{t "torrent-easy"}} </b> {{t "torrent-run"}}</p> \n')

lines.append('  <hr> \n')
lines.append('  <p> {{t "torrent-magnet"}}  <b> {{t "torrent-maglink"}} </b> {{t "torrent-magopen"}}  </p> \n')
lines.append('  <p> <hr> </p> \n')

lines.append('  <div class ="col-md-4" > \n')
lines.append('  <p> {{fa-icon "envelope"}} <a href = "mailto:{{' + "'skylinescondor@gmail.com'}}" + '"> {{t "contact-admin"}} </a> {{" "}} {{t "contact-torrents"}} </p>   \n')
lines.append('  </div> \n')
lines.append('  <p> <hr> </p> \n')

lines.append('<table class="table table-striped"> \n')
lines.append('  <thead> \n')
lines.append('        <th class="column-buttons"> {{t "download-torrent"}}</th> \n')
lines.append('        <th class="column-buttons"></th> \n')
lines.append('        <th class="column-buttons"></th> \n')
lines.append('  </thead> \n')

lines.append('  <tbody> \n')

for i, name in enumerate(names):
    lines.append('\t<tr> \n')
    lines.append('\t\t<td> <a href="http://199.192.98.227:8080/landscapes-zip/{}.torrent" download>'.format(name) + ' {{fa-icon "download" size="sm"}}' + ' {} </a> </td> \n'.format(name.replace('.7z','')))
    magfilepath = dir+'/{}.magnet'.format(name)
    # print magfilepath
    if os.path.exists(magfilepath):
        print name, readfileNoStrip(magfilepath)
        magline = readfileNoStrip(magfilepath)[0].strip() + trackerStr
        # print 'mag',magline
        lines.append('\t<td> <a href={} download> magnet </a> </td> '.format(magline))
    sizeStr = '{:.1f} GB"'.format(sizes[i] /float(10 ** 9))
    lines.append('\t\t<td align = "right"> {{"' + sizeStr  + '}} </td> \n')
    lines.append('\t</tr> \n\n')

lines.append('  </tbody> \n')
lines.append(' </table> \n')

lines.append('</BasePage> \n')

file = open(landPage, 'w')
file.writelines(lines)
file.close()
