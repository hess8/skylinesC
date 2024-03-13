import os, sys
sys.path.append('/home/bret/servers/repo-skylinesC/skylinesC/skylines')
from common import readfileNoStrip

trackerStr = "&tr=http://tracker.opentrackr.org:1337/announce"
landPage = '/home/bret/servers/repo-skylinesC/skylinesC/ember/app/templates/landscapes.hbs'
dir = '/media/sf_landscapes-zip'
dirlist = os.listdir(dir)
names = []
sizes = []
for item in dirlist:
    if item.split('.')[-1]=='torrent':
        name = item.split('.torrent')[0]
        names.append(name)
        sizes.append (os.stat('{}/{}'.format(dir,name)).st_size)
# print names

lines = []
lines.append('<BasePage> \n')

lines.append('  <div class="page-header"> \n')
lines.append('    <h1>{{t "landscapes"}}</h1> \n')
lines.append('  </div> \n')

lines.append('  <p>  <b> {{t "landscapesPage.before"}}  {{t "install"}} qBittorrent  {{t "landscapesPage.other"}} </b> </p> \n')
# lines.append('  <p> <a href="/files/qbittorrent_x64_setup.exe" class="btn btn-default" download>{{fa-icon "download" size="lg"}} {{t "download"}} qBittorrent</a> </p> \n')
lines.append('  <p> {{t "landscapesPage.many"}} {{t "landscapesPage.magnet"}} </p> \n')
lines.append('  <p> {{t "landscapesPage.makeSure"}} <b> {{t "not"}} {{t "your"}} {{t "browser"}}. </b>  {{t "landscapesPage.limits"}}  </p> \n')
lines.append('  <p> {{t "landscapesPage.extract-with"}}  <a href="https://www.7-zip.org/download.html"> 7-zip </a>. {{t "landscapesPage.extract-here"}} {{t "landscapesPage.paste"}} </p> \n')
lines.append('  <p> {{t "landscapesPage.download"}} </p> \n')
lines.append('  <div class ="col-md-4" > \n')
lines.append('  <p> {{fa-icon "envelope"}} <a href = "mailto:{{' + "'skylinescondor@gmail.com'}}" + '"> {{t "contact-admin"}} </a> {{" "}} {{t "landscapesPage.contact"}} </p>   \n')
lines.append('  </div> \n')
lines.append('  <hr> \n')
lines.append('  <p> <b> {{t "landscapesPage.host"}} </b> {{t "landscapesPage.seed"}} <b> {{t "landscapesPage.easy"}} </b> {{t "landscapesPage.run"}}</p> \n')

lines.append('  <p> <hr> </p> \n')

lines.append('<table class="table table-striped"> \n')
lines.append('  <thead> \n')
# lines.append('        <th class="column-buttons"> {{t "download-torrent"}}</th> \n')
# lines.append('        <th class="column-buttons"></th> \n')
# lines.append('        <th class="column-buttons"></th> \n')
lines.append('  </thead> \n')

lines.append('  <tbody> \n')

lines.append('  <p> {{t "landscapesPage.see"}}  <a href="https://www.condor.club/sceneriesmap/241/"> {{t "landscapesPage.map"}} </a>  {{t "landscapesPage.locations"}} </p> \n')

for i, name in enumerate(names):
    lines.append('\t<tr> \n')
    magfilepath = dir+'/{}.magnet'.format(name)
    # print name
    try:
        magline = readfileNoStrip(magfilepath)[0].strip() + trackerStr
    except:
        xx=0
    lines.append('\t\t<td> <a href="{}">'.format(magline) + ' {{fa-icon "download" size="sm"}}' + ' {} </a> </td> \n'.format(name.replace('.7z','')))
    # lines.append('\t<td> <a href="{}"> magnet </a> </td> '.format(magline))
    GiB = 1.074e+9
    if sizes[i] > 0.1 * GiB:
        sizeStr = '{:.1f} GB"'.format(sizes[i] / GiB)
    else:
        sizeStr = '{:.1f} MB"'.format(sizes[i] / GiB * 1000)
    lines.append('\t<td align = "right"> {{"' + sizeStr  + '}} </td> \n')
    lines.append('\t</tr> \n\n')

lines.append('  </tbody> \n')
lines.append(' </table> \n')

lines.append('</BasePage> \n')

file = open(landPage, 'w')
file.writelines(lines)
file.close()
print('New landscapes page created for {} files'.format(len(names)))
