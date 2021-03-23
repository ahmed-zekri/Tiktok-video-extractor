import os
import pathlib
import subprocess
import time
import tkinter as tk
import concurrent.futures
import dropbox as dropbox
import requests
from datetime import datetime
from TikTokApi import TikTokApi
from selenium import webdriver
# from pydrive.auth import GoogleAuth
# from pydrive.drive import GoogleDrive
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options

hashtag_input = None
like_input = None
browser = None
days_input = None
service = None
info = None
Client_SECRET_FILE = 'client_secrets.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']


def upload_video_to_drive(file):
    # id_folder = None
    print(f'Uploading {file.split("/")[1]} to dropbox please wait')
    # # To create a new folder
    # folders = drive.ListFile({"q": "mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()
    # for folder in folders:
    #     if folder['title'] == file.split('/')[0]:
    #         id_folder = folder['id']
    #         break
    #
    # if id_folder is None:
    #     new_folder = drive.CreateFile(
    #         {'title': file.split('/')[0], 'mimeType': 'application/vnd.google-apps.folder'})
    #     new_folder.Upload()
    #     id_folder = new_folder['id']
    #
    # file1 = drive.CreateFile({'title': file.split('/')[1], 'parents': [{'id': id_folder}]})
    # file1.SetContentFile(file)
    # file1.Upload()  # Files.insert()
    #
    # print(f'File {file.split("/")[1]} uploaded successfully')
    # file name
    # path object, defining the file

    # target location in Dropbox
    target = "/"  # the target folder
    # the target path and file name

    # Create a dropbox object using an API v2 key

    # open the file and upload it
    with open(file, "rb") as f:
        # upload gives you metadata about the file
        # we want to overwite any previous version of the file
        d.files_upload(f.read(), f'/{file}', mute=True)
    print(f'File {file.split("/")[1]} uploaded successfully')

    # create a shared link
    # link = d.sharing_create_shared_link(targetfile)

    # url which can be shared
    # url = link.url

    # link which directly downloads by replacing ?dl=0 with ?dl=1
    # dl_url = re.sub(r"\?dl\=0", "?dl=1", url)
    # print(dl_url)


def timer(time_count, current_time):
    printed_time = 0
    while True:
        if printed_time != int(time.perf_counter() - current_time):
            printed_time = int(time.perf_counter() - current_time)
            print(printed_time)

        if printed_time >= time_count:
            break


def download_video(url, count, last_index=False, from_sample=False, name=None):
    if name is not None:
        print(f'Attempting to download {name}, {count} videos downloaded so far')
    browser.get('https://ssstik.io/')
    print('Waiting for 8 seconds this is necessary to avoid server ban ')
    current_time = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(timer, 8, current_time)
    time.sleep(8)
    text_url = browser.find_element_by_id('main_page_text')
    if info is not None:
        info.config(text=f"Downloading video number {str(count)} please wait ...")

    text_url.send_keys(url)

    text_submit = browser.find_element_by_id('submit')
    text_submit.click()
    print('Submit button clicked ')
    print('Waiting for 8 seconds this is necessary to avoid server ban ')
    current_time = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(timer, 8, current_time)
    time.sleep(8)

    while True:
        try:
            browser.find_elements_by_xpath("//*[contains(text(), 'Without watermark [2]')]")[0].click()

            # browser.find_element_by_xpath('//*[@title="Download Server 02"]').click()
            break
        except NoSuchElementException:
            pass
    main_handler = browser.current_window_handle
    if from_sample:
        return
    print('Waiting for 3 seconds this is necessary to avoid server ban ')
    current_time = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(timer, 3, current_time)
    time.sleep(3)

    for handle in browser.window_handles:
        if handle != browser.current_window_handle:
            browser.switch_to.window(handle)
            video_url = browser.current_url

            browser.close()
            browser.switch_to.window(main_handler)

            break
    print(f'Video found downloading {name} please wait')
    r = requests.get(video_url, allow_redirects=True)
    if not os.path.exists(f'{name.split("_")[0]}'):
        os.makedirs(f'{name.split("_")[0]}')
    with open(f'{name.split("_")[0]}/{name}.mp4', "wb") as f:
        f.write(r.content)

    print(f'{str(count + 1)} File(s) downloaded sucessfully')
    upload_video_to_drive(f'{name.split("_")[0]}/{name}.mp4')

    # print(f'{url} {name}')

    # info.config(text=f"Downloading File {str(count + 1)}")
    # subprocess.run([
    #     'youtube-dl.exe', url, '--output', f'{name.split("_")[0]}/{name}.mp4'],
    #     check=True, )
    # upload_video_to_drive(f'{name.split("_")[0]}/{name}.mp4')
    #
    # if last_index:
    #     info.config(text=f"All downloads completed successfully")


def extract_videos():
    global info
    global days_input
    days_allowed = 10000
    try:
        days_allowed = int(days_input.get())
    except:
        pass
    info.config(text=f"Exporting videos info to a txt file, this will take a moment")
    videos_list = []
    hashtags_list = hashtag_input.get().split(',')
    # Hashtag_search
    for hashtag in hashtags_list:
        print(f'extracting 2000 videos with hashtag \"{hashtag}\" please wait this will take 1 minute approximately')

        videos = api.byHashtag(hashtag, count=2000)

        if len(videos) == 0:
            return
            # loop through the videos
        with open('ticktock.txt', 'w', encoding="utf-8") as opened_file:
            for video in videos:
                days_since_creation = (datetime.now() - datetime.fromtimestamp(video['createTime'])).days
                if int(days_since_creation <= days_allowed):
                    if video['stats']['diggCount'] > int(like_input.get()):
                        opened_file.write(
                            f'https://www.tiktok.com/@{video["author"]["uniqueId"]}/video/{video["video"]["id"]}  ; Author: {video["author"]["uniqueId"]} \n')
                    videos_list.append(
                        f'https://www.tiktok.com/@{video["author"]["uniqueId"]}/video/{video["video"]["id"]}&&{hashtag}&&{video["author"]["uniqueId"]}&&{video["video"]["id"]}&&{video["createTime"]}')

    print(
        f'{len(videos_list)} videos found uploaded in the recent {str(days_allowed)} day(s) with minimum likes {like_input.get()}')

    info.config(text=f"Videos infos exported to ticktock.txt downloading videos now ")
    videos_list.sort(key=lambda x: int(x.split('&&')[4]), reverse=True)
    for count, video_item in enumerate(videos_list):
        download_video(video_item.split('&&')[0], count, last_index=(count == len(videos_list) - 1),
                       name=f'{video_item.split("&&")[1]}_{video_item.split("&&")[2]}_{video_item.split("&&")[3]}')
    if len(videos_list) > 0:
        info.config(text=f"Downloading Finished,Downloaded {len(videos_list)}")
        print(f"Downloading Finished,Downloaded {len(videos_list)}")
    else:
        print(f"No video found matching your criteria")
        info.config(text=f"No video found matching your criteria")


def tkinter_create_window():
    global days_input
    global hashtag_input
    global like_input
    global info
    window = tk.Tk()
    # window initialisation
    window.geometry("350x200")
    window.winfo_toplevel().title("Tiktok scraper")

    # Hashtags label
    hashtags_label = tk.Label(text="Enter hashtags separated by commas like this ,")
    # Hashtag input
    hashtag_input = tk.Entry()
    # Minimum likes label
    likes_label = tk.Label(text="Minimum likes")
    # Minimum likes Input
    like_input = tk.Entry()
    # Minimum days label
    days_label = tk.Label(text="Specify the number of days allowed since video uploaded")
    # Minimum days Input
    days_input = tk.Entry()
    # Extract data button
    button = tk.Button(text="Extract videos", command=extract_videos)
    info = tk.Label(text="", fg='#0000CD')
    # error = tk.Label(text="", fg='#f00')
    # info2 = tk.Label(text="", fg='#008000')
    # include widgets in ui
    hashtags_label.pack()
    hashtag_input.pack()
    likes_label.pack()
    like_input.pack()
    days_label.pack()
    days_input.pack()
    button.pack(pady=10, side=tk.TOP)
    # error.pack(pady=5, side=tk.TOP)
    # info2.pack(pady=7, side=tk.TOP)
    info.pack(pady=5, side=tk.TOP)

    window.resizable(False, False)
    window.attributes("-topmost", True)
    window.mainloop()


def initialize_selinuim():
    global browser
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2)  # custom location
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', '/tmp')
    options = Options()
    options.headless = False
    profile.set_preference(
        'browser.helperApps.neverAsk.saveToDisk',
        'application/vnd.hzn-3d-crossword;video/3gpp;video/3gpp2;application/vnd.mseq;application/vnd.3m.post-it-notes;application/vnd.3gpp.pic-bw-large;application/vnd.3gpp.pic-bw-small;application/vnd.3gpp.pic-bw-var;application/vnd.3gp2.tcap;application/x-7z-compressed;application/x-abiword;application/x-ace-compressed;application/vnd.americandynamics.acc;application/vnd.acucobol;application/vnd.acucorp;audio/adpcm;application/x-authorware-bin;application/x-athorware-map;application/x-authorware-seg;application/vnd.adobe.air-application-installer-package+zip;application/x-shockwave-flash;application/vnd.adobe.fxp;application/pdf;application/vnd.cups-ppd;application/x-director;applicaion/vnd.adobe.xdp+xml;application/vnd.adobe.xfdf;audio/x-aac;application/vnd.ahead.space;application/vnd.airzip.filesecure.azf;application/vnd.airzip.filesecure.azs;application/vnd.amazon.ebook;application/vnd.amiga.ami;applicatin/andrew-inset;application/vnd.android.package-archive;application/vnd.anser-web-certificate-issue-initiation;application/vnd.anser-web-funds-transfer-initiation;application/vnd.antix.game-component;application/vnd.apple.installe+xml;application/applixware;application/vnd.hhe.lesson-player;application/vnd.aristanetworks.swi;text/x-asm;application/atomcat+xml;application/atomsvc+xml;application/atom+xml;application/pkix-attr-cert;audio/x-aiff;video/x-msvieo;application/vnd.audiograph;image/vnd.dxf;model/vnd.dwf;text/plain-bas;application/x-bcpio;application/octet-stream;image/bmp;application/x-bittorrent;application/vnd.rim.cod;application/vnd.blueice.multipass;application/vnd.bm;application/x-sh;image/prs.btif;application/vnd.businessobjects;application/x-bzip;application/x-bzip2;application/x-csh;text/x-c;application/vnd.chemdraw+xml;text/css;chemical/x-cdx;chemical/x-cml;chemical/x-csml;application/vn.contact.cmsg;application/vnd.claymore;application/vnd.clonk.c4group;image/vnd.dvb.subtitle;application/cdmi-capability;application/cdmi-container;application/cdmi-domain;application/cdmi-object;application/cdmi-queue;applicationvnd.cluetrust.cartomobile-config;application/vnd.cluetrust.cartomobile-config-pkg;image/x-cmu-raster;model/vnd.collada+xml;text/csv;application/mac-compactpro;application/vnd.wap.wmlc;image/cgm;x-conference/x-cooltalk;image/x-cmx;application/vnd.xara;application/vnd.cosmocaller;application/x-cpio;application/vnd.crick.clicker;application/vnd.crick.clicker.keyboard;application/vnd.crick.clicker.palette;application/vnd.crick.clicker.template;application/vn.crick.clicker.wordbank;application/vnd.criticaltools.wbs+xml;application/vnd.rig.cryptonote;chemical/x-cif;chemical/x-cmdf;application/cu-seeme;application/prs.cww;text/vnd.curl;text/vnd.curl.dcurl;text/vnd.curl.mcurl;text/vnd.crl.scurl;application/vnd.curl.car;application/vnd.curl.pcurl;application/vnd.yellowriver-custom-menu;application/dssc+der;application/dssc+xml;application/x-debian-package;audio/vnd.dece.audio;image/vnd.dece.graphic;video/vnd.dec.hd;video/vnd.dece.mobile;video/vnd.uvvu.mp4;video/vnd.dece.pd;video/vnd.dece.sd;video/vnd.dece.video;application/x-dvi;application/vnd.fdsn.seed;application/x-dtbook+xml;application/x-dtbresource+xml;application/vnd.dvb.ait;applcation/vnd.dvb.service;audio/vnd.digital-winds;image/vnd.djvu;application/xml-dtd;application/vnd.dolby.mlp;application/x-doom;application/vnd.dpgraph;audio/vnd.dra;application/vnd.dreamfactory;audio/vnd.dts;audio/vnd.dts.hd;imag/vnd.dwg;application/vnd.dynageo;application/ecmascript;application/vnd.ecowin.chart;image/vnd.fujixerox.edmics-mmr;image/vnd.fujixerox.edmics-rlc;application/exi;application/vnd.proteus.magazine;application/epub+zip;message/rfc82;application/vnd.enliven;application/vnd.is-xpr;image/vnd.xiff;application/vnd.xfdl;application/emma+xml;application/vnd.ezpix-album;application/vnd.ezpix-package;image/vnd.fst;video/vnd.fvt;image/vnd.fastbidsheet;application/vn.denovo.fcselayout-link;video/x-f4v;video/x-flv;image/vnd.fpx;image/vnd.net-fpx;text/vnd.fmi.flexstor;video/x-fli;application/vnd.fluxtime.clip;application/vnd.fdf;text/x-fortran;application/vnd.mif;application/vnd.framemaker;imae/x-freehand;application/vnd.fsc.weblaunch;application/vnd.frogans.fnc;application/vnd.frogans.ltf;application/vnd.fujixerox.ddd;application/vnd.fujixerox.docuworks;application/vnd.fujixerox.docuworks.binder;application/vnd.fujitu.oasys;application/vnd.fujitsu.oasys2;application/vnd.fujitsu.oasys3;application/vnd.fujitsu.oasysgp;application/vnd.fujitsu.oasysprs;application/x-futuresplash;application/vnd.fuzzysheet;image/g3fax;application/vnd.gmx;model/vn.gtw;application/vnd.genomatix.tuxedo;application/vnd.geogebra.file;application/vnd.geogebra.tool;model/vnd.gdl;application/vnd.geometry-explorer;application/vnd.geonext;application/vnd.geoplan;application/vnd.geospace;applicatio/x-font-ghostscript;application/x-font-bdf;application/x-gtar;application/x-texinfo;application/x-gnumeric;application/vnd.google-earth.kml+xml;application/vnd.google-earth.kmz;application/vnd.grafeq;image/gif;text/vnd.graphviz;aplication/vnd.groove-account;application/vnd.groove-help;application/vnd.groove-identity-message;application/vnd.groove-injector;application/vnd.groove-tool-message;application/vnd.groove-tool-template;application/vnd.groove-vcar;video/h261;video/h263;video/h264;application/vnd.hp-hpid;application/vnd.hp-hps;application/x-hdf;audio/vnd.rip;application/vnd.hbci;application/vnd.hp-jlyt;application/vnd.hp-pcl;application/vnd.hp-hpgl;application/vnd.yamaha.h-script;application/vnd.yamaha.hv-dic;application/vnd.yamaha.hv-voice;application/vnd.hydrostatix.sof-data;application/hyperstudio;application/vnd.hal+xml;text/html;application/vnd.ibm.rights-management;application/vnd.ibm.securecontainer;text/calendar;application/vnd.iccprofile;image/x-icon;application/vnd.igloader;image/ief;application/vnd.immervision-ivp;application/vnd.immervision-ivu;application/reginfo+xml;text/vnd.in3d.3dml;text/vnd.in3d.spot;mode/iges;application/vnd.intergeo;application/vnd.cinderella;application/vnd.intercon.formnet;application/vnd.isac.fcs;application/ipfix;application/pkix-cert;application/pkixcmp;application/pkix-crl;application/pkix-pkipath;applicaion/vnd.insors.igm;application/vnd.ipunplugged.rcprofile;application/vnd.irepository.package+xml;text/vnd.sun.j2me.app-descriptor;application/java-archive;application/java-vm;application/x-java-jnlp-file;application/java-serializd-object;text/x-java-source,java;application/javascript;application/json;application/vnd.joost.joda-archive;video/jpm;image/jpeg;video/jpeg;application/vnd.kahootz;application/vnd.chipnuts.karaoke-mmd;application/vnd.kde.karbon;aplication/vnd.kde.kchart;application/vnd.kde.kformula;application/vnd.kde.kivio;application/vnd.kde.kontour;application/vnd.kde.kpresenter;application/vnd.kde.kspread;application/vnd.kde.kword;application/vnd.kenameaapp;applicatin/vnd.kidspiration;application/vnd.kinar;application/vnd.kodak-descriptor;application/vnd.las.las+xml;application/x-latex;application/vnd.llamagraphics.life-balance.desktop;application/vnd.llamagraphics.life-balance.exchange+xml;application/vnd.jam;application/vnd.lotus-1-2-3;application/vnd.lotus-approach;application/vnd.lotus-freelance;application/vnd.lotus-notes;application/vnd.lotus-organizer;application/vnd.lotus-screencam;application/vnd.lotus-wordro;audio/vnd.lucent.voice;audio/x-mpegurl;video/x-m4v;application/mac-binhex40;application/vnd.macports.portpkg;application/vnd.osgeo.mapguide.package;application/marc;application/marcxml+xml;application/mxf;application/vnd.wolfrm.player;application/mathematica;application/mathml+xml;application/mbox;application/vnd.medcalcdata;application/mediaservercontrol+xml;application/vnd.mediastation.cdkey;application/vnd.mfer;application/vnd.mfmp;model/mesh;appliation/mads+xml;application/mets+xml;application/mods+xml;application/metalink4+xml;application/vnd.ms-powerpoint.template.macroenabled.12;application/vnd.ms-word.document.macroenabled.12;application/vnd.ms-word.template.macroenabed.12;application/vnd.mcd;application/vnd.micrografx.flo;application/vnd.micrografx.igx;application/vnd.eszigno3+xml;application/x-msaccess;video/x-ms-asf;application/x-msdownload;application/vnd.ms-artgalry;application/vnd.ms-ca-compressed;application/vnd.ms-ims;application/x-ms-application;application/x-msclip;image/vnd.ms-modi;application/vnd.ms-fontobject;application/vnd.ms-excel;application/vnd.ms-excel.addin.macroenabled.12;application/vnd.ms-excelsheet.binary.macroenabled.12;application/vnd.ms-excel.template.macroenabled.12;application/vnd.ms-excel.sheet.macroenabled.12;application/vnd.ms-htmlhelp;application/x-mscardfile;application/vnd.ms-lrm;application/x-msmediaview;aplication/x-msmoney;application/vnd.openxmlformats-officedocument.presentationml.presentation;application/vnd.openxmlformats-officedocument.presentationml.slide;application/vnd.openxmlformats-officedocument.presentationml.slideshw;application/vnd.openxmlformats-officedocument.presentationml.template;application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;application/vnd.openxmlformats-officedocument.spreadsheetml.template;application/vnd.openxmformats-officedocument.wordprocessingml.document;application/vnd.openxmlformats-officedocument.wordprocessingml.template;application/x-msbinder;application/vnd.ms-officetheme;application/onenote;audio/vnd.ms-playready.media.pya;vdeo/vnd.ms-playready.media.pyv;application/vnd.ms-powerpoint;application/vnd.ms-powerpoint.addin.macroenabled.12;application/vnd.ms-powerpoint.slide.macroenabled.12;application/vnd.ms-powerpoint.presentation.macroenabled.12;appliation/vnd.ms-powerpoint.slideshow.macroenabled.12;application/vnd.ms-project;application/x-mspublisher;application/x-msschedule;application/x-silverlight-app;application/vnd.ms-pki.stl;application/vnd.ms-pki.seccat;application/vn.visio;video/x-ms-wm;audio/x-ms-wma;audio/x-ms-wax;video/x-ms-wmx;application/x-ms-wmd;application/vnd.ms-wpl;application/x-ms-wmz;video/x-ms-wmv;video/x-ms-wvx;application/x-msmetafile;application/x-msterminal;application/msword;application/x-mswrite;application/vnd.ms-works;application/x-ms-xbap;application/vnd.ms-xpsdocument;audio/midi;application/vnd.ibm.minipay;application/vnd.ibm.modcap;application/vnd.jcp.javame.midlet-rms;application/vnd.tmobile-ivetv;application/x-mobipocket-ebook;application/vnd.mobius.mbk;application/vnd.mobius.dis;application/vnd.mobius.plc;application/vnd.mobius.mqy;application/vnd.mobius.msl;application/vnd.mobius.txf;application/vnd.mobius.daf;tex/vnd.fly;application/vnd.mophun.certificate;application/vnd.mophun.application;video/mj2;audio/mpeg;video/vnd.mpegurl;video/mpeg;application/mp21;audio/mp4;video/mp4;application/mp4;application/vnd.apple.mpegurl;application/vnd.msician;application/vnd.muvee.style;application/xv+xml;application/vnd.nokia.n-gage.data;application/vnd.nokia.n-gage.symbian.install;application/x-dtbncx+xml;application/x-netcdf;application/vnd.neurolanguage.nlu;application/vnd.na;application/vnd.noblenet-directory;application/vnd.noblenet-sealer;application/vnd.noblenet-web;application/vnd.nokia.radio-preset;application/vnd.nokia.radio-presets;text/n3;application/vnd.novadigm.edm;application/vnd.novadim.edx;application/vnd.novadigm.ext;application/vnd.flographit;audio/vnd.nuera.ecelp4800;audio/vnd.nuera.ecelp7470;audio/vnd.nuera.ecelp9600;application/oda;application/ogg;audio/ogg;video/ogg;application/vnd.oma.dd2+xml;applicatin/vnd.oasis.opendocument.text-web;application/oebps-package+xml;application/vnd.intu.qbo;application/vnd.openofficeorg.extension;application/vnd.yamaha.openscoreformat;audio/webm;video/webm;application/vnd.oasis.opendocument.char;application/vnd.oasis.opendocument.chart-template;application/vnd.oasis.opendocument.database;application/vnd.oasis.opendocument.formula;application/vnd.oasis.opendocument.formula-template;application/vnd.oasis.opendocument.grapics;application/vnd.oasis.opendocument.graphics-template;application/vnd.oasis.opendocument.image;application/vnd.oasis.opendocument.image-template;application/vnd.oasis.opendocument.presentation;application/vnd.oasis.opendocumen.presentation-template;application/vnd.oasis.opendocument.spreadsheet;application/vnd.oasis.opendocument.spreadsheet-template;application/vnd.oasis.opendocument.text;application/vnd.oasis.opendocument.text-master;application/vnd.asis.opendocument.text-template;image/ktx;application/vnd.sun.xml.calc;application/vnd.sun.xml.calc.template;application/vnd.sun.xml.draw;application/vnd.sun.xml.draw.template;application/vnd.sun.xml.impress;application/vnd.sun.xl.impress.template;application/vnd.sun.xml.math;application/vnd.sun.xml.writer;application/vnd.sun.xml.writer.global;application/vnd.sun.xml.writer.template;application/x-font-otf;application/vnd.yamaha.openscoreformat.osfpvg+xml;application/vnd.osgi.dp;application/vnd.palm;text/x-pascal;application/vnd.pawaafile;application/vnd.hp-pclxl;application/vnd.picsel;image/x-pcx;image/vnd.adobe.photoshop;application/pics-rules;image/x-pict;application/x-chat;aplication/pkcs10;application/x-pkcs12;application/pkcs7-mime;application/pkcs7-signature;application/x-pkcs7-certreqresp;application/x-pkcs7-certificates;application/pkcs8;application/vnd.pocketlearn;image/x-portable-anymap;image/-portable-bitmap;application/x-font-pcf;application/font-tdpfr;application/x-chess-pgn;image/x-portable-graymap;image/png;image/x-portable-pixmap;application/pskc+xml;application/vnd.ctc-posml;application/postscript;application/xfont-type1;application/vnd.powerbuilder6;application/pgp-encrypted;application/pgp-signature;application/vnd.previewsystems.box;application/vnd.pvi.ptid1;application/pls+xml;application/vnd.pg.format;application/vnd.pg.osasli;tex/prs.lines.tag;application/x-font-linux-psf;application/vnd.publishare-delta-tree;application/vnd.pmi.widget;application/vnd.quark.quarkxpress;application/vnd.epson.esf;application/vnd.epson.msf;application/vnd.epson.ssf;applicaton/vnd.epson.quickanime;application/vnd.intu.qfx;video/quicktime;application/x-rar-compressed;audio/x-pn-realaudio;audio/x-pn-realaudio-plugin;application/rsd+xml;application/vnd.rn-realmedia;application/vnd.realvnc.bed;applicatin/vnd.recordare.musicxml;application/vnd.recordare.musicxml+xml;application/relax-ng-compact-syntax;application/vnd.data-vision.rdz;application/rdf+xml;application/vnd.cloanto.rp9;application/vnd.jisp;application/rtf;text/richtex;application/vnd.route66.link66+xml;application/rss+xml;application/shf+xml;application/vnd.sailingtracker.track;image/svg+xml;application/vnd.sus-calendar;application/sru+xml;application/set-payment-initiation;application/set-reistration-initiation;application/vnd.sema;application/vnd.semd;application/vnd.semf;application/vnd.seemail;application/x-font-snf;application/scvp-vp-request;application/scvp-vp-response;application/scvp-cv-request;application/svp-cv-response;application/sdp;text/x-setext;video/x-sgi-movie;application/vnd.shana.informed.formdata;application/vnd.shana.informed.formtemplate;application/vnd.shana.informed.interchange;application/vnd.shana.informed.package;application/thraud+xml;application/x-shar;image/x-rgb;application/vnd.epson.salt;application/vnd.accpac.simply.aso;application/vnd.accpac.simply.imp;application/vnd.simtech-mindmapper;application/vnd.commonspace;application/vnd.ymaha.smaf-audio;application/vnd.smaf;application/vnd.yamaha.smaf-phrase;application/vnd.smart.teacher;application/vnd.svd;application/sparql-query;application/sparql-results+xml;application/srgs;application/srgs+xml;application/sml+xml;application/vnd.koan;text/sgml;application/vnd.stardivision.calc;application/vnd.stardivision.draw;application/vnd.stardivision.impress;application/vnd.stardivision.math;application/vnd.stardivision.writer;application/vnd.tardivision.writer-global;application/vnd.stepmania.stepchart;application/x-stuffit;application/x-stuffitx;application/vnd.solent.sdkm+xml;application/vnd.olpc-sugar;audio/basic;application/vnd.wqd;application/vnd.symbian.install;application/smil+xml;application/vnd.syncml+xml;application/vnd.syncml.dm+wbxml;application/vnd.syncml.dm+xml;application/x-sv4cpio;application/x-sv4crc;application/sbml+xml;text/tab-separated-values;image/tiff;application/vnd.to.intent-module-archive;application/x-tar;application/x-tcl;application/x-tex;application/x-tex-tfm;application/tei+xml;text/plain;application/vnd.spotfire.dxp;application/vnd.spotfire.sfs;application/timestamped-data;applicationvnd.trid.tpt;application/vnd.triscape.mxs;text/troff;application/vnd.trueapp;application/x-font-ttf;text/turtle;application/vnd.umajin;application/vnd.uoml+xml;application/vnd.unity;application/vnd.ufdl;text/uri-list;application/nd.uiq.theme;application/x-ustar;text/x-uuencode;text/x-vcalendar;text/x-vcard;application/x-cdlink;application/vnd.vsf;model/vrml;application/vnd.vcx;model/vnd.mts;model/vnd.vtu;application/vnd.visionary;video/vnd.vivo;applicatin/ccxml+xml,;application/voicexml+xml;application/x-wais-source;application/vnd.wap.wbxml;image/vnd.wap.wbmp;audio/x-wav;application/davmount+xml;application/x-font-woff;application/wspolicy+xml;image/webp;application/vnd.webturb;application/widget;application/winhlp;text/vnd.wap.wml;text/vnd.wap.wmlscript;application/vnd.wap.wmlscriptc;application/vnd.wordperfect;application/vnd.wt.stf;application/wsdl+xml;image/x-xbitmap;image/x-xpixmap;image/x-xwindowump;application/x-x509-ca-cert;application/x-xfig;application/xhtml+xml;application/xml;application/xcap-diff+xml;application/xenc+xml;application/patch-ops-error+xml;application/resource-lists+xml;application/rls-services+xml;aplication/resource-lists-diff+xml;application/xslt+xml;application/xop+xml;application/x-xpinstall;application/xspf+xml;application/vnd.mozilla.xul+xml;chemical/x-xyz;text/yaml;application/yang;application/yin+xml;application/vnd.ul;application/zip;application/vnd.handheld-entertainment+xml;application/vnd.zzazz.deck+xml')
    browser = webdriver.Firefox(options=options, firefox_profile=profile, executable_path=r'geckodriver.exe')

    # download  a sample video to show the ad as the ad only be shown one time
    # download_video("https://www.tiktok.com/@sindahani/video/6933555023276182789", 0, last_index=False, from_sample=True)


if __name__ == '__main__':
    url = 'https://v39-eu.tiktokcdn.com/473bab26c5c16127ef5e40153ba913c2/60593ca8/video/tos/useast2a/tos-useast2a-pve-0068/1a26ba14ce9d4dcba7ac8c67d0e7f578/?a=1233&br=722&bt=361&cd=0%7C0%7C0&ch=0&cr=0&cs=0&cv=1&dr=0&ds=6&er=&l=2021032218552301011515311212289D59&lr=all&mime_type=video_mp4&net=0&pl=0&qs=0&rc=amt4Zjw4aGh2NDMzOTczM0ApODs4Ojo5ZTw2NzU1NTU0PGdlLS1gcTZwazVgLS1iMTZzczVfLzQ2YDZhM2MyLjRfMF46Yw%3D%3D&vl=&vr='

    d = dropbox.Dropbox(
        'lxvoM1hkhw0AAAAAAAAAAajf03WF1bSYiz9Mm84B88XlhvniePTg3UDkjnuTCfct')
    # service = Create_Service(Client_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    # gauth = GoogleAuth()
    # gauth.LocalWebserverAuth()
    #
    # drive = GoogleDrive(gauth)

    # file1['title'] = 'HelloWorld.txt'  # Change title of the file
    # file1.Upload() # Files.patch()
    #
    # content = file1.GetContentString()  # 'Hello'
    # file1.SetContentString(content+' World!')  # 'Hello World!'
    # file1.Upload() # Files.update()
    #
    # file2 = drive.CreateFile()
    # file2.SetContentFile('hello.png')
    # file2.Upload()
    # print('Created file %s with mimeType %s' % (file2['title'],
    #                                             file2['mimeType']))
    # # Created file hello.png with mimeType image/png
    #
    # file3 = drive.CreateFile({'id': file2['id']})
    # print('Downloading file %s from Google Drive' % file3['title']) # 'hello.png'
    # file3.GetContentFile('world.png')  # Save Drive file as a local file

    # or download Google Docs files in an export format provided.
    # downloading a docs document as an html file:

    # Initialize selenium
    initialize_selinuim()

    # initialize tiktok api
    api = TikTokApi.get_instance()
    # api.get_Video_By_DownloadURL("https://www.tiktok.com/@bouhmid576/video/6940552531063950598")

    # Create Ui
    tkinter_create_window()
