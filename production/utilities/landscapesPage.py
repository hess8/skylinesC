def landscapesPage(zipDir,landPageDest,landHBS,qbtExePath,trackerStr):
    '''Called by updateZipped.py'''
    import os, sys
    sys.path.append('/mnt/L/condor-related/skylinesC/skylines')
    from common_util import copy_file_to_guest, readfile, readfileNoStrip, writefile

    def column_table_head(version):
        lines.append('     <div class="column"> \n')
        lines.append('       <table class="table table-striped"> \n')
        lines.append('       <thead> <h4>Condor ' + str(version) + ' {{t "landscapes"}}</h4> </thead>\n')
        lines.append('       <tbody> \n')
        # lines.append('        <th class="column-buttons"> {{t "download-torrent"}}</th> \n')
        # lines.append('        <th class="column-buttons"></th> \n')
        # lines.append('        <th class="column-buttons"></th> \n')

    def tableRow():
        lines.append('\t<tr> \n')
        magfilepath = zipDir + os.sep + '{}.magnet'.format(name)
        try:
            magline = readfileNoStrip(magfilepath)[0].strip() + trackerStr
        except:
            xx=0
        lines.append('\t\t\t\t<td> <a href="{}">'.format(magline) + ' {{fa-icon "download" size="sm"}}' + ' {} </a> </td> \n'.format(name.replace('.7z','')))
        # lines.append('\t<td> <a href="{}"> magnet </a> </td> '.format(magline))
        GiB = 1.074e+9
        size = os.stat(os.path.join(zipDir, name)).st_size
        if size > 0.1 * GiB:
            sizeStr = '{:.1f} GB"'.format(size / GiB)
        else:
            sizeStr = '{:.1f} MB"'.format(size / GiB * 1000)
        lines.append('\t<td align = "right"> {{"' + sizeStr  + '}} </td> \n')
        lines.append('\t</tr> \n\n')

    def column_table_end():
        lines.append('       </tbody> \n')
        lines.append('       </table> \n')
        lines.append('     </div> \n')

    dirlist = os.listdir(zipDir)
    names = []
    sizes = []
    for item in dirlist:
        if 'AA3' in item and item.split('.')[-1]=='torrent':
            xx=0
        if item.split('.')[-1]=='torrent':
            name = item.split('.torrent')[0]
            names.append(name)

    lowVersionList = []
    highVersionList = []
    for i, name in enumerate(names):
        if '_C3' in name:
            highVersionList.append(name)
        else:
            lowVersionList.append(name)

    lines = []
    lines.append('<BasePage> \n')

    lines.append('  <div class="page-header"> \n')
    lines.append('    <h1>{{t "landscapes"}}</h1> \n')
    lines.append('  </div> \n')

    lines.append('  <p>  <b> {{t "landscapesPage.before"}}  {{t "install"}} qBittorrent  {{t "landscapesPage.other"}} </b> </p> \n')
    # lines.append('  <p> <a href="/files/qbittorrent_x64_setup.exe" class="btn btn-default" download>{{fa-icon "download" size="lg"}} {{t "download"}} qBittorrent</a> </p> \n')
    exeStr = '  <p> <a href="' + qbtExePath + '" class="btn btn-default">{{fa-icon "download" size="lg"}} {{t "download"}} qBittorrent</a> </p> \n'
    lines.append(exeStr)
    lines.append('  <p> {{t "landscapesPage.many"}} {{t "landscapesPage.magnet"}} </p> \n')
    lines.append('  <p> {{t "landscapesPage.makeSure"}} <b> {{t "not"}} {{t "your"}} {{t "browser"}}. </b>  {{t "landscapesPage.limits"}}  </p> \n')
    lines.append('  <p> {{t "landscapesPage.extract-with"}}  <a href="https://www.7-zip.org/download.html"> 7-zip </a>. {{t "landscapesPage.extract-here"}} {{t "landscapesPage.paste"}} </p> \n')
    lines.append('  <p> {{t "landscapesPage.download"}} </p> \n')
    lines.append('  <div class ="col-md-4" > \n')
    lines.append('  <p> {{fa-icon "envelope"}} <a href = "mailto:{{' + "'skylinescondor@gmail.com'}}" + '"> {{t "contact-admin"}} </a> {{" "}} {{t "landscapesPage.contact"}} </p>   \n')
    lines.append('  </div> \n')
    lines.append('  <hr> \n')
    lines.append('  <p> <b> {{t "landscapesPage.host"}} </b> {{t "landscapesPage.seed"}} <b> {{t "landscapesPage.easy"}} </b> {{t "landscapesPage.run"}}</p> \n')

    lines.append('  <hr> \n')
    lines.append('  <p> {{t "landscapesPage.see"}}  <a href="https://www.condor.club/sceneriesmap/241/"> {{t "landscapesPage.map"}} </a>  {{t "landscapesPage.locations"}} </p> \n')

    lines.append('  <p> <hr> </p> \n')

    lines.append('  <style> \n')
    lines.append('  * {box-sizing: border-box;} \n')
    lines.append('  .row {display: flex;} \n')
    lines.append('  .column { \n')
    lines.append('   width: 330px; \n')
    lines.append('   padding: 20px; \n')
    lines.append('   } \n')
    lines.append('   </style> \n')

    lines.append(' <div class="row"> \n')
    column_table_head('2')
    for i, name in enumerate(lowVersionList):
        tableRow()
    column_table_end()

    column_table_head('3')
    for i, name in enumerate(highVersionList):
        tableRow()
    column_table_end()
    lines.append(' </div> \n')
    lines.append('</BasePage> \n')
    writefile(lines,landPageDest)
    [username,passwd] = readfile('/home/bret/.local/secure/userU')
    copy_file_to_guest('U14 (SkylinesC server on Z) Current', landPageDest, landHBS, username, passwd)
    print('New landscapes page created for {} files'.format(len(names)))
