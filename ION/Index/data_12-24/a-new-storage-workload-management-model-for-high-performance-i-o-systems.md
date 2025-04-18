# *A New Storage Workload Management Model for High-performance I/O Systems*

*Huang Huang College of Computer, National University of Defense Technology, Changsha 410073, China National Supercomputer Center in Changsha, Changsha 410082, China hugh_0108@163.com*

# *Sheng You **

*National Supercomputer Center in Changsha, Changsha 410082, China yousheng@hnu.edu.cn*

*Abstract***²'DWDLQWHQVLYH DSSOLFDWLRQV LQYROYH ZLWK PDVVLYH GDWDUDQJLQJIURPWHUDE\WHVWRSHWDE\WHVZKLFKLVDFULWLFDO ERWWOHQHFNLQWKHQH[WJHQHUDWLRQV\VWHPV,QWKLVDUWLFOHZH PDLQO\IRFXVRQV\VWHP,2FRPSHWLWLRQFDXVHGE\WKHGDWD LQWHQVLYHDSSOLFDWLRQVDQGXQEDODQFHG VWRUDJHFDSDFLW\DQG DWWHPSW WR GHYHORS HIIHFWLYH VROXWLRQV WR DOOHYLDWH WKLVLVVXH 7R WKLV HQG ZH GHYHORS DQ ,2 PLGGOHZDUH EDVHG PHWKRG 7KH FRUH RI RXU PLGGOHZDUH LV WKH VWRUDJH ZRUNORDG PDQDJHPHQWPRGHO6:00ZKLFKDOORZVXVWRDGMXVWDQG RSWLPL]H WKH ,2 DFFHVV SURFHVV HIILFLHQWO\ DQG IOH[LEO\:H KDYHLPSOHPHQWHGRXUVROXWLRQDQGFRQGXFWHGH[WHQVLYHWHVWV EDVHG RQ D SHWDVFDOH V\VWHP 7KH H[SHULPHQWDO UHVXOWV GHPRQVWUDWHWKHHIIHFWLYHQHVV DQGHIILFLHQF\RIRXUVROXWLRQ**

*Keywords-supercomputer; I/O performance; storage workload management;*

#### , ,1752'8&7,21

([DVFDOH V\VWHPV SURYLGH DQ XQSUHFHGHQWHG RSSRUWXQLW\IRUVFLHQWLILFFRPSXWLQJ,QWKHPHDQZKLOHWKH SDUDOOHO,2VUHTXLUHPHQWVLQVXFKV\VWHPVDUHDOVRKHDYLO\ DJJUDYDWHGDQGKDYHEHFRPHDPDMRUERWWOHQHFNLQPDQ\ VFLHQWLILF FRPSXWLQJ WDVNV &XUUHQWO\ GDWDLQWHQVLYH VFLHQWLILF DSSOLFDWLRQV FDQ LQYROYH WHUDE\WHV RI LQSXW DQG RXWSXWGDWD>@7KHVHDSSOLFDWLRQVUDQJLQJIURPVPDOO WR ODUJHVFDOH VLPXODWLRQV DUH XVXDOO\ KDQGOLQJ WKH ,2 RSHUDWLRQVWKURXJKWKH0HVVDJH3DVVLQJ ,QWHUIDFHLQWKHLU DSSOLFDWLRQ ,QWKLV FDVHLWLVKLJKO\ FRVWWRSHUIRUP VXFK WDVNV DFURVV D QHWZRUN ZLWK D ODUJH QXPEHU RI VPDOO ,2 UHTXHVWV7KH03,,2OD\HULVUHVSRQVLEOHIRUDFFHVVLQJWKH ILOH V\VWHPV DQG IRU RSWLPL]LQJ WKH ,2 RSHUDWLRQV RI WKH WDVNV(VVHQWLDOO\LWLVGHSHQGHQWRQWKHSDUWRIWKH03, VWDQGDUG UHODWHG WR ,2 ZKLFK GHVFULEHV KRZ WR SHUIRUP GDWDUHDGDQGZULWHRSHUDWLRQVWRSDUDOOHOILOHV\VWHPVHJ /XVWUHDQG*3)6

$V PHQWLRQHG HDUOLHU WKH GDWDLQWHQVLYH DSSOLFDWLRQV LQYROYHPDVVLYHDPRXQWVRIGDWDUDQJLQJIURPWHUDE\WHVWR SHWDE\WHV ZKLFK LV D FULWLFDO ERWWOHQHFN LQ WKH 1H[W *HQHUDWLRQ V\VWHPV ,Q WKH PHDQZKLOH WKH XQHYHQ GLVWULEXWLRQ RI PDVVLYH GDWD RFFXUV IUHTXHQWO\ LQ KLJK SHUIRUPDQFH FRPSXWLQJ :LWK WKH LQFUHDVLQJ VFDOH RI VWRUDJH V\VWHP LW PD\ JUHDWO\ DIIHFW WKH SHUIRUPDQFH RI WKH ZKROH V\VWHP $QG XQEDODQFHG VWRUDJH FDSDFLW\ ZLOO

## *YuTong Lu*

*School of Data and Computer Science, Sun Yat-Sen University, Guangzhou 510006, China National Supercomputer Center in Guangzhou, Guangzhou 510006*

DJJUDYDWH WKLV SKHQRPHQRQ ,Q WKLV DUWLFOH ZH PDLQO\ IRFXV RQ V\VWHP ,2 SHUIRUPDQFH FDXVHG E\ WKH GDWD LQWHQVLYH DSSOLFDWLRQV DQG XQEDODQFHG VWRUDJH FDSDFLW\ DQGDWWHPSWWRGHYHORSHIIHFWLYHVROXWLRQVWRDOOHYLDWHWKLV LVVXH

*HQHUDOO\ WKLV SDSHU SURSRVHV D VWRUDJH PLGGOHZDUH EDVHGPHWKRGWRDFKLHYHWKHJRDO$WDKLJKOHYHOWKH,2 PLGGOHZDUH LV SODFHG DW WKH PLGGOH OD\HU RI WKH ,2 VRIWZDUH VWDFN DQGLW PDLQO\ VHUYHV DV D FRQQHFWLQJ OLQN EHWZHHQ D KLJKOHYHO ,2 OLEUDU\ DQG WKH SDUDOOHO ILOH V\VWHP 6SHFLILFDOO\ WKH FRUH RI RXU PLGGOHZDUH LV WKH VWRUDJH ZRUNORDG PDQDJHPHQW PRGHO 6:00 ZKLFK FRQVLVWVRIWKUHHPDMRUPRGXOHV ,2SDWKRSWLPL]DWLRQ PRGXOH  VWRUDJH FDSDFLW\ HTXDOL]DWLRQ PRGXOH :LWK WKHVHPRGXOHVLWDOORZVXVWRDGMXVWDQGRSWLPL]HWKH,2 DFFHVVSURFHVVHIILFLHQWO\DQGIOH[LEO\DFKLHYLQJIDYRUDEOH V\VWHP SHUIRUPDQFH7R VXPPDUL]HWKLV SDSHUPDNHVWKH IROORZLQJPDLQFRQWULEXWLRQV

 :H SUHVHQW D PLGGOHZDUHEDVHG VROXWLRQ WR LPSURYHWKHSHUIRUPDQFHRIGDWDLQWHQVLYHDSSOLFDWLRQV

 :H FRQGXFW H[WHQVLYH H[SHULPHQWV EDVHG RQ WKH 0LON\:D\$7+$ WR GHPRQVWUDWH WKH HIIHFWLYHQHVV DQGHIILFLHQF\RIRXUSURSRVHGVROXWLRQ

7KHUHVWRIWKHSDSHULVRUJDQL]HGDVIROORZV6HFWLRQ,, FRYHUVVRPHEDFNJURXQGV6HFWLRQ,,, SUHVHQWVRXUVROXWLRQ 6HFWLRQ ,9 SUHVHQWV H[SHULPHQWDO UHVXOWV DQG GLVFXVVLRQV )LQDOO\ZHFRQFOXGHWKLVSDSHULQ6HFWLRQ9

## ,, %$&.*5281'

7REHWWHUXQGHUVWDQGWKHUHVWRIRXUSDSHULWLVKHOSIXO WRLQWURGXFHVRPHEDFNJURXQGVUHODWHGWR03,,2SDUDOOHO GLVWULEXWHG ILOH V\VWHPV ZRUNORDG PDQDJHU DQG PDQ\ RWKHU WHFKQLTXHV XVHG LQ VXSHUFRPSXWHUV DQGRU RWKHU FOXVWHUV

#### *A. ROMIO, Lustre, and SLURM*

$ W\SLFDO H[DPSOH RI 03,,2 LV WKH 520,2 >@ ZKLFK LV D KLJKSHUIRUPDQFH SRUWDEOH LPSOHPHQWDWLRQ RI 03,,2*HQHUDOO\LWLVGHVLJQHGWREHXVHGZLWKDQ\03, LPSOHPHQWDWLRQDQGLVRSWLPL]HGIRUQRQFRQWLJXRXVDFFHVV SDWWHUQVE\DWHFKQLTXHFDOOHGWKHWZRSKDVH,2ZKLFKLV FRPPRQ LQ GDWDLQWHQVLYH SDUDOOHO DSSOLFDWLRQV 2Q WKH RWKHU KDQG D W\SLFDO H[DPSOH RI SDUDOOHO GLVWULEXWHG ILOH V\VWHPVLV/XVWUH >@ZKLFKLVGHVLJQHGWR VROYHPDVVLYH VWRUDJH SUREOHPV DQG JHQHUDOO\ LV XVHG IRU KLJK SHUIRUPDQFH FRPSXWLQJ +3& $ /XVWUH ILOH V\VWHP KDV WKUHH PDMRU IXQFWLRQDO XQLWV  PHWDGDWD VHUYHUV 0'6 ZKLFK XVHV PHWDGDWD WDUJHW 0'7 GHYLFHV WR VWRUH QDPHVSDFH PHWDGDWD  REMHFW VWRUDJH VHUYHU 266 ZKLFK VWRUHV ILOH GDWD RQ REMHFW VWRUDJH WDUJHW 267 GHYLFHV DQG  ILOH V\VWHP FOLHQWV ZKLFK DFFHVV DQG KDQGOHWKHGDWD*HQHUDOO\/XVWUHDOORZVWKHDSSOLFDWLRQWR VHWWKHVWULSHDWWULEXWHZKLFKFRQVLVWVRIVWULSHVL]HVWULSH FRXQWDQGWKH267LQGH[RIILUVWVWULSH8VXDOO\DIWHUWKH ILOHLVFUHDWHGHJLQ)LJXUHWKHVWULSHVL]HFRXOGQRWEH PRGLILHG IXUWKHU 6SHFLILFDOO\ /XVWUH DVVLJQV VWULSHV WR 267V XVLQJHLWKHUD URXQGURELQDOJRULWKP RUD ZHLJKWHG DOJRULWKP %\ GHIDXOW ZKHQ WKH IUHH VSDFH DFURVV 267V GLIIHUVE\PRUHWKDQLWLV FDOOHGLPEDODQFHG ,QWKLV FDVHWKHZHLJKWHGDOJRULWKPLVXVHGWRUDQGRPO\VHOHFWWKH QH[W 267 ZKLFK KDV PRUH IUHH VSDFH 7KLV HVVHQWLDOO\ VDFULILFHV WKH ILOH V\VWHP SHUIRUPDQFH EHIRUH WKH VSDFH XWLOL]DWLRQLV UHEDODQFHG DJDLQ )XUWKHUPRUHWKH 6/850 LV D W\SLFDO ZRUNORDG PDQDJHU XVHG E\ PDQ\ RI WKH VXSHUFRPSXWHUVDQGRWKHUFOXVWHUV >@$PDMRU IHDWXUHRI 6/850 LV WKDW LW SURYLGHV D IUHH DQG RSHQVRXUFH MRE VFKHGXOHU WR VHUYLFH 7KH 6/850 KDV DOVR WKUHH RWKHU IHDWXUHV  LW DOORFDWHV H[FOXVLYH DQGRU QRQH[FOXVLYH DFFHVV WR FRPSXWHU QRGHV WR XVHUV IRU SHUIRUP MRE  LW SURYLGHV D IUDPHZRUN IRU VWDUWLQJ H[HFXWLQJ DQG PDQDJLQJ MRE RQ D VHW RI DOORFDWHG QRGHV DQG  LW DUELWUDWHVFRQWHQWLRQIRUUHVRXUFHVE\VHWWLQJWKHSULRULW\RI DSHQGLQJMREV8VXDOO\LWXVHVDEHVWILWDOJRULWKPEDVHG RQ+LOEHUWFXUYHDQGIDWWUHHQHWZRUNWRSRORJ\WRRSWLPL]H UHVRXUFH VFKHGXOLQJ DQG WDVN DVVLJQPHQWV RQ VXSHUFRPSXWHUV

# *B. Storage Resources and Resource Management System*

$V WKH H[DVFDOH FRPSXWLQJ PD\ SURGXFH PDVVLYH DPRXQWVRIGDWDWKHVWRUDJHV\VWHPLVXVXDOO\GHVLJQHGWR EH YHU\ KXJH $V D UHVXOWWKH VWRUDJH UHVRXUFHVPDVWHUHG E\ QH[W JHQHUDWLRQ V\VWHPV EHFRPH UHODWLYHO\ ULFK >@ )XUWKHUPRUH ZLWKWKH DEXQGDQW FRPSXWLQJ UHVRXUFHVWKH VWRUDJHUHVRXUFHVPD\DOVRQHHGDFHQWUDOL]HGPDQDJHPHQW DQG UHTXLUH VRPH UHVRXUFH VFKHGXOLQJ LQ V\VWHPV 7\SLFDOO\ WKH VWRUDJH UHVRXUFHV DUH VFKHGXOHG E\ WKH XQGHUO\LQJPHFKDQLVPRIILOHV\VWHPV6XFKRSHUDWLRQVDUH XVXDOO\WUDQVSDUHQWWRWKH XVHU,WLVUHDVRQDEOHWRVFKHGXOH WKHVFDUFHUHVRXUFHVE\WKHXQGHUO\LQJPHFKDQLVPVRIILOH V\VWHP +RZHYHU DV IRU WKH V\VWHPV ZKHUH KXQGUHGV RI VWRUDJH VHUYHUVDQGWKRXVDQGV RI VWRUDJHREMHFWVFRXOGEH DYDLODEOHWKDWLVVWRUDJHUHVRXUFHVZLOOEHFRPHYHU\ULFK ,Q WKLV FDVH LW LV QHFHVVDU\ WR XVH VWRUDJH PDQDJHPHQW V\VWHPV IRUVFKHGXOLQJ >@0HDQZKLOHLWLVHQFRXUDJHG WRDFKLHYHVWRUDJHUHVRXUFHYLVXDOL]DWLRQVLQFHLWFDQDOORZ XVHUV WR KDYH HQRXJK FKRLFHV EHWZHHQ XSORDGLQJGRZQORDGLQJ GDWD DQG UXQQLQJ ,2 LQWHQVLYH DSSOLFDWLRQV,Q/XVWUHILOHV\VWHPVWKHVWULSHSURYLGHGE\ $3,VLVRQHRIVWRUDJHUHVRXUFHV:KHQ\RXVHWXSWKHILOH VWULSLQJDQGSDUDPHWHU YDOXHVD JRRG UXOHRIWKXPELVWR VHW VWULSH RYHU DV IHZ REMHFWV DV SRVVLEOH RQO\ LI WKHVH REMHFWVFDQVDWLVI\WKHUHTXLUHPHQWVLQVWHDGRIXVLQJPXFK REMHFWV 7KH WUDGLWLRQDO UHVRXUFH PDQDJHPHQW V\VWHP LV DFWLQJ EHWZHHQ WKH XVHU DQG WKH FRPSXWLQJ UHVRXUFHV EHWZHHQ WKH DGPLQLVWUDWRU DQG WKH FRPSXWLQJ UHVRXUFHV DQGEHWZHHQWKHDGPLQLVWUDWRUDQGWKHXVHU >@)URPWKH XVHU
VSRLQWRIYLHZWKHFOXVWHUV\VWHPLVMXVWOLNHDVHUYHU RU3&ZKLFKFDQEHDYDLODEOH IRUPDQ\XVHUVDWWKHVDPH WLPH :KHQ WKH QXPEHU RI XVHUV ZKR XVH WKH FOXVWHU LQFUHDVHVWKHV\VWHPUHVRXUFHVDUHDOVRJUDGXDOO\GHSOHWHG 5HVRXUFH PDQDJHPHQW LV WR FROOHFW WKH MRE LQIRUPDWLRQ VXEPLWWHG E\ XVHUV DQG UHDVRQDEO\ DOORFDWH UHVRXUFHV WR HDFKMREVRDVWRHQVXUHWKDWWKHFRPSXWLQJSRZHURIWKH FOXVWHU V\VWHP LV IXOO\ XWLOL]HG DQG WKH FRPSXWLQJ UHVXOWV DUHREWDLQHGDVVRRQDVSRVVLEOH

## ,,, 2850(7+2'

)LJXUH SORWV WKH RYHUDOO IUDPHZRUN RI RXU VROXWLRQ 7KH FRUH FRQWULEXWLRQ RI RXU VROXWLRQ LV WKH ,2 PLGGOHZDUH ZKLFK LV SODFHG DW WKH PLGGOH OD\HU RI WKH DUFKLWHFWXUH ,Q WKH PLGGOHZDUH ZH GHYHORS D VWRUDJH ZRUNORDGPDQDJHPHQWPRGHO 6:00 ZKLFKLV VKRZQ LQ)LJXUH

![](_page_1_Figure_6.png)

)LJXUH ,2VRIWZDUHVWDFNDUFKLWHFWXUH

7KH 6:00 LV WKHRUHWLFDOO\ GHVLJQHG WR VROYH FRQJHVWLRQ SUREOHPV FDXVHG E\ D ODUJH QXPEHU RI ,2 UHTXHVWVDQGWRRSWLPL]HWKHVFKHGXOLQJSURFHVVRIVWRUDJH UHVRXUFHV ZKHQ ZH VLPXOWDQHRXVO\ UXQ VRPH RI ,2 LQWHQVLYH DSSOLFDWLRQV 7KH 6:00 FRQVLVWV RI WKUHH PRGXOHV

- x ,2SDWKRSWLPL]DWLRQPRGXOH
- x 6WRUDJHFDSDFLW\HTXDOL]DWLRQPRGXOH

7KURXJK WKHVH WKUHH PDMRU PRGXOHV 6:00 FDQ  TXHU\WKHMREVLWXDWLRQIURPWKHMREUHVRXUFHPDQDJHPHQW V\VWHP6/850VHQVHWKHXVDJHVWDWXVRIWKHVWRUDJH UHVRXUFHIURPWKHILOHV\VWHP/XVWUHVRDVWRUHDVRQDEO\ VFKHGXOH WKH UHVRXUFHV 1H[W ZH GLVFXVV HDFK PDMRU PRGXOHLQGHWDLO

#### *A. I/O Path Optimization Module*

,W LV HDV\ WR XQGHUVWDQG WKDW ZKHQ PXOWLSOH ,2 LQWHQVLYHDSSOLFDWLRQVLQLWLDWH,2UHTXHVWVDWWKHVDPHWLPH WKLV VKDOOFDXVH ,2 FRPSHWLWLRQ DQGWKXVGHJUDGHWKH ,2 SHUIRUPDQFH RI WKH V\VWHP >@ $OOHYLDWLQJ ,2 FRPSHWLWLRQ DQG DOORFDWLQJ UHDVRQDEOH VFKHGXOH ,2 UHVRXUFHV EHFRPHV WKH NH\ RI SRLQW WR DFKLHYH D JRRG V\VWHPSHUIRUPDQFH6:00LVDVWRUDJHPLGGOHZDUHWKDW UHSODFHV WKH ILOH V\VWHP WR WDNH RYHU WKH ,2 SDWK PDQDJHPHQW IXQFWLRQDQG DOORFDWHVWKH VWRUDJH UHVRXUFHV ZKHQPXOWLSOHMREVLQLWLDWH ,2 UHTXHVWVDWWKH VDPHWLPH *HQHUDOO\ ZKHQ D MRE LV VXEPLWWHG WR WKH MRE UHVRXUFH

PDQDJHPHQWV\VWHPWKHLQIRUPDWLRQRIWKHMREWKDWQHHGV WRFDOOODUJHVFDOH,2VZLOOEHVHQWWRWKH6:00ZKLFK VKDOO VSHFLI\ WKH ,2 SDWK IRU WKH FRUUHVSRQGLQJMRE 7KH DOORFDWHG VWRUDJH UHVRXUFHV IROORZ WKH SULQFLSOH RI PLQLPXP RYHUODS DQG RSWLPL]H WKH ,2 DJJUHJDWLRQ EDQGZLGWKWRPDNHLWPRUHHIILFLHQWO\ZKLOHVDWLVI\LQJWKH RSHUDWLRQDO UHTXLUHPHQWV RI HDFK MRE 0RUH VSHFLILFDOO\ WKH ,2LV UHTXLUHGWRDOLJQWKH VWULSH ERXQGDULHVWR DYRLG WKH RYHUKHDG RI XQQHFHVVDU\ ORFN FRQWHQWLRQ :KHQ WZR SURFHVVHVZULWHDVWULSHDWWKHVDPHWLPHWKH,2HIILFLHQF\ ZLOO EHDIIHFWHG E\ HDFK RWKHU 6R ZH UHFRPPHQG VHWWLQJ XSDVWULSHRUWZRVWULSHVWRDFFHVVRQDQ,2SURFHVVRQD VLQJOHVHUYHU6HFRQGO\ZKHQGLIIHUHQWXVHUV¶DSSOLFDWLRQV RFFXS\ WKH VWULSHV UHVRXUFHV DUH WR EH UHGLVWULEXWHG YLD 6:00VRDVWRVDWLVI\WKHSULQFLSOHRIPLQLPXPRYHUODS ,Q VKRUW ZKHQ GLIIHUHQWDSSOLFDWLRQ SURFHVVHV DUH UHDGLQJ DQG ZULWLQJ ZH QHHG WR FRQWURO ERWK WKH QXPEHU RI RFFXSLHG VWULSHVDQGWKH QXPEHURIRYHUODSSLQJ VWULSHVDW WKH VDPHWLPH UDWKHUWKDQ DGRSWLQJWKH H[WUHPH PHWKRGV VXFK DV FRPSOHWH RYHUODS RU QR RYHUODS7KLV ZD\LW FDQ PLQLPL]H WKH LQWHUDFWLRQ DQG LPSURYH WKH UHDGZULWH HIILFLHQF\

![](_page_2_Figure_1.png)

)LJXUH 6WRUDJHZRUNORDG PDQDJHPHQW PRGHO 6:00DUFKLWHFWXUH

#### *B. Storage Capacity Equalization Module*

,QDQ SHWDVFDOH V\VWHPVWRUDJHGHYLFHVPD\IDFHVRPH VSHFLDO FRQGLWLRQV VXFK DV SDUWLDO GHYLFH IDLOXUH GHYLFH FDSDFLW\ H[SDQVLRQ WKH FUHDWLRQ RI VRPH XQXVXDOO\ ODUJH ILOHV DQG WKH ZURQJ EDQG SDUDPHWHUV HWF ZKLFK HDVLO\ OHDGWRWKHLPEDODQFHRIGDWDFDSDFLW\ >@

'XULQJ WKH SDVW VHYHUDO \HDUV PDQ\ VROXWLRQV KDYH EHHQ SURSRVHG WR WDFNOH WKH ORDG LPEDODQFH LVVXH RI SDUDOOHO ILOH V\VWHPV >@ :H UHFRPPHQGWKHFDSDFLW\ EDODQFLQJ PDQDJHPHQW LQ LGOH WLPH WR HQVXUHWKH VWRUDJH HIILFLHQF\ LQ EXV\ WLPH DQG ZH SURSRVH D VHW RI ,2 UHVRXUFH UHEDODQFLQJ PHWKRG EDVHG RQ EXV\ WLPH DSSOLFDWLRQ WR DOOHYLDWH ,2 FRPSHWLWLRQ EHWZHHQ DSSOLFDWLRQV 0RUH VSHFLILFDOO\ ZH GR DV $OJRULWKP $PRQJ WKHP6 LVWKHJURXSLQJRIVWULSHVWKDWHDFKJURXS FRQWDLQV VHYHUDO FRQVHFXWLYH VWULSHV DQG2 LVWKH RYHUODS RIPXOWLSOH,2WDVNV )LUVWO\WKHUHDGLQJDQGZULWLQJRIWKH VWULSH VKRXOG EH LQ UHYHUVH RUGHU ,Q RWKHU ZRUGV LWLVWR VHOHFW WKH EHJLQQLQJ ZLWK WKH VWULSH WKDW LV ODUJHVW LQGH[ QXPEHU7KLVDOORZVWKHODWHVWDGGHGGHYLFHVWREDODQFHWKH JOREDO VWRUDJH FDSDFLW\ DV TXLFNO\ DV SRVVLEOH 6HFRQGO\ ZH WU\ WR HQVXUH WKH FRQWLQXLW\ RI WKH GLVWULEXWLRQ RI WKH VWULSH0HDQZKLOHWKHVWULSH LVGLYLGHGLQWREORFNVWRPDUN WKHSHUFHQWDJHRIVWRUDJHFDSDFLW\RFFXSLHGDQGZHVHWWKH RYHUODSRIPXOWLSOH,2WDVNVUXQQLQJRQWKHEORFNZLWKWKH ORZHVW SHUFHQWDJH RFFXSDQF\ )LQDOO\ WKH FDSDFLW\ EDODQFLQJPDQDJHPHQW LVFDUULHGRXWRQVWRUDJH UHVRXUFHV E\VHOHFWLQJWKHLGOHSHULRGRI,2UDWKHUWKDQFRQVLGHULQJ FDSDFLW\EDODQFLQJZKHQ,2LVEXV\

#### $/*25,7+0 ,

| ,QSXWJURXSLQJRIVWULSHVHW6 RYHUODSSLQJVHWRIZRUNV2 |
| --- |
| 2XWSXWSDUWLWLRQVHWRIRYHUODSSLQJLQVWULSHJURXS3 |
| LQ 6 GR IRUHDFK JURXSLQJRIVWULSH V L |
|  &RPSXWLQJWKHDYHUDJHFDSDFLW\RI V L |
| HQGIRU |
|  &RPSXWLQJWKHRYHUODSSLQJFRHIILFLHQWRI M R |
| 6RUWLQJ V LQDVFHQGLQJRUGHU L |
| 6RUWLQJ M R LQGHVFHQGLQJRUGHU |
| IRUHDFK RYHUODSSLQJ M R LQ2 GR |
| LQ6 GR IRUHDFK JURXSLQJRIVWULSH V L |
| 3XW M R LQ L V |
| L |
| HQGIRU |
| HQGIRU |
| UHWXUQ 3 |
|  L R V M |

#### ,9 (;3(5,0(176

#### *A. Experimental Environments*

7RLQYHVWLJDWH6:00IXQFWLRQZH SHUIRUPHGDVHWRI H[SHULPHQWV RQ ODUJHVFDOH /XVWUH ILOH V\VWHPV EDVHG RQ WKH 0LON\:D\$ 7+$ DW WKH 1DWLRQDO 6XSHUFRPSXWLQJ&HQWHU LQ&KDQJVKD16&& 0LON\:D\ $ LVDPDWXUHFRPPHUFLDOVXSHUFRPSXWLQJV\VWHP ,WVILOH V\VWHPV DUH KHDYLO\ XWLOL]HG E\ QXPHURXV VFLHQWLILF FRPSXWLQJ DQGUHVHDUFK RSWLRQVZKLFK PDNHLWLPSRVVLEOH IRURXUH[SHULPHQWVWREHWHVWHGH[FOXVLYHO\ :HXVHGWKH 0LON\:D\$ FOXVWHU WKDW FRQVLVWHG RI FRPSXWH QRGHV HDFKZLWKWZR FRUH,QWHO ;SURFHVVRUVDQG *LJDE\WHRIPHPRU\7KHFRPSXWH QRGHVZHUHFRQQHFWHG WR/XVWUHWKURXJK3'3KLJKVSHHGLQWHUFRQQHFWLRQ >@ 7KH/XVWUHILOH V\VWHP FRQVLVWHGRI VHUYHUVUXQQLQJ5HG +DW(QWHUSULVH/LQX[ IRUDFDSDFLW\RI 7HUDE\WHV 7KHUH DUH D WRWDO QXPEHU RI 267V DQG 0'7V 7KH 03, LPSOHPHQWDWLRQ XVHG RQ 0LON\:D\$ ZDV 03,&+ 7KH ERWWOHQHFN LQ WKH V\VWHP ZDV D *LJDE\WH SHU VHFRQG WKURXJKSXW IURP ,2 QHWZRUN 7KH ,/2 FKDUDFWHULVWLFV RI RWKHUMREV ZLOO FDXVH WKH FRQWHQWLRQ GXULQJRXUH[SHULPHQWV 2XUH[SHULPHQWDWLRQ ZDV EXLOW DQ ,2 LQWHQVLYH HQYLURQPHQW VR ZH EHOLHYH WKDW WKH UHVXOWV REWDLQHGKHUHFDQUHIOHFW WKHUHODWHGFRQWHQWVHPERGLHGLQ ,2 LQWHQVLYH DSSOLFDWLRQV DQG ILOH V\VWHPV LQ UHDO HQYLURQPHQWV

## *B. Results and Discussions*

:H FRQGXFW WKUHH JURXSV RI H[SHULPHQWV  ([S WHVWV WKH HIIHFWLYHQHVV RI 6:00 EDVHG RQ WKUHH DSSOLFDWLRQV LQFOXGLQJ ,25VKDUHG ,25DOO DQG 7HVW,2 XVLQJ DQG ZLWKRXW XVLQJ 6:00  ([S VWXGLHV WKH FKDQJHVLQ WHUPVRI WKHVWRUDJHFDSDFLW\GLVWULEXWLRQ XVLQJ DQGZLWKRXWXVLQJ6:00IRUDORQJSHULRG

$V IRU WKHVH WKUHH DSSOLFDWLRQV ,25VKDUHG ,25DOO DQG 7HVW,2 WKH\ UHSUHVHQW WKUHHW\SLFDO SDWWHUQV IRU ,2 LQWHQVLYHDSSOLFDWLRQV,25VKDUHGUHDGLQJDQGZULWLQJ WR D ODUJH ILOH DW WKH VDPH WLPH  ,25DOO UHDGLQJ DQG ZULWLQJ WR PXOWLSOH VPDOO ILOHV VLPXOWDQHRXVO\ DQG  7HVW,2WKLVLVDWHVWDSSOLFDWLRQZHFUHDWHGIRU7HVW,2DQG LW VLPXODWHV D K\EULG ,2 DSSOLFDWLRQ IRU UHDGLQJ DQG ZULWLQJDODUJH ILOHDQG VHYHUDO VPDOO ILOHV2QHRIWHVWVLV WR UXQ DOO RI WKH DSSOLFDWLRQV DW WKH VDPH WLPH DQG WR VFKHGXOH VWRUDJH UHVRXUFHVWKURXJK 6:00 7KH RWKHULV WR UXQ WKHVH DSSOLFDWLRQV RQ WKH H[LVWLQJ HQYLURQPHQW ZLWKRXW XVLQJ 6:00 7KH VDPH LV WKDW ERWK JURXSV RI WHVWV ZLOO EHLQWHUIHUHG E\ YDULRXV UXQQLQJ SURJUDPV7KH GLIIHUHQFH LV WKDW WKH H[SHULPHQWDO JURXS VFKHGXOHG E\ 6:00ZLOODGRSWWKHRQHWRWZRPRGHDQG'DUVKDQZLOO UHFRUGWKH,2SURFHVVLQGHWDLODQG FROOHFWUHOHYDQWGDWDWR FRPSOHWHWKHLUWDVNV ZLWK DPRUH EDODQFHG GLVWULEXWLRQ RI UHVRXUFHV:HVHWWKHWRWDOQXPEHURISURFHVVHVLQWKHWKUHH WHVW DSSOLFDWLRQVWR DQG UHVSHFWLYHO\)RU HDFK SURFHVV LQ WKH H[SHULPHQW UHDG DQG ZULWH UHVRXUFHV DUH VFKHGXOHGYLD6:00DQGWKH\ZLOOEHDVVLJQHGWKHPRVW DSSURSULDWH QXPEHU RI VWULSHV :H FKDQJHG WKUHH NH\ SDUDPHWHUV LQ WKH H[SHULPHQWV FRQGXFWHG RQ 0LON\:D\ $7+$7KHQXPEHURISURFHVVRUVLQWKHRSHUDWLRQ  WKH QXPEHU RI VWULSHV DQG WKH ILOH VL]H :H QRWH WKDW HDFK SURFHVVRU ZURWH *LJDE\WH RI GDWD WR GLVN DUUD\ 7KXV WKH ILOH VL]H YDULHG EHWZHHQ *LJDE\WHV DQG 7HUDE\WH:HNHSWWKHQXPEHURI267VFRQVWDQWDWDQG PDLQWDLQHG D VWULSH VL]H RI 0HJDE\WH (DFK GDWD SRLQW UHSUHVHQWVWKHPHDQYDOXHRIWULDOV

$V FDQ EH VHHQ LQ )LJXUH WKH XVH RI 6:00 WR RSWLPL]H ,2 SDWKV UHVXOWHGLQ KLJKHU ZULWH EDQGZLGWK ,Q DGGLWLRQ LW FDQ EH VHHQ IURP WKH UHVXOWV WKDW WKH ZULWH RSHUDWLRQRIWKHRSHUDWLRQJURXS VFKHGXOLQJZLWK6:00 FDQ JHW KLJKHU EDQGZLGWK DQG HIIHFWLYHO\ LPSURYH WKH RSHUDWLRQ HIILFLHQF\ :RUNLQJ JURXSV WKDW GLG QRW XVH 6:00 GLG QRW KDYH D EDODQFHG GLVWULEXWLRQ RI VWRUDJH UHVRXUFHV UHVXOWLQJ LQ XQGHUXWLOL]DWLRQ RI EDQGZLGWK UHVRXUFHV :HFDQDOVRVHHIURP)LJXUHV DDQGEWKDW WKH ZULWH EDQGZLGWK LPSURYHPHQW LV OLPLWHG ZKHQ WKH QXPEHU RI SURFHVVHV LV VPDOO )URP WKH H[SHULPHQWDO UHVXOWVRI )LJXUH FZHFDQVHHWKDWWKHZULWHRSHUDWLRQ RI PXOWLSOH VPDOO ILOHV DFKLHYHV EHWWHU UHVXOWV LQ WKH SDWK RSWLPL]DWLRQ RI 6:00 :LWK WKH KHOS RI 6:00 WKH WKUHH DSSOLFDWLRQV JRW WKH RSWLPDO ZULWH EDQGZLGWK SURPRWLRQ UHVSHFWLYHO\ ZKHQ WKH WRWDO QXPEHU RI SURFHVVHVZDV

![](_page_3_Figure_6.png)

:H FRQWLQXRXVO\ UHFRUGHG FKDQJHV LQ WKH VWRUDJH FDSDFLW\GLVWULEXWLRQIRUVL[PRQWKV7KHILUVWWKUHHPRQWKV ZHUH UHFRUGHG DQG REVHUYHG DFFRUGLQJ WR WKH GHIDXOW FRQILJXUDWLRQ 7KH ODVW WKUHH PRQWKV ZHUH UHFRUGHG DQG REVHUYHG XQGHU WKH FRQGLWLRQ RI 6:00 )LJXUH D VKRZVWKHVWRUDJHFDSDFLW\EHIRUHFDSDFLW\EDODQFLQJZLWK 6:00 DQG DIWHU WKUHH PRQWKV RI FRQWLQXRXV RSHUDWLRQ )LJXUH E VKRZV WKH GLVWULEXWLRQ RI VWRUDJH FDSDFLW\ FKDQJHVDURXQGWKUHHPRQWKVXVLQJGHIDXOWFRQILJXUDWLRQ

,Q WKHVH H[SHULPHQWV ZH FDQ XQGHUVWDQG WKDW WKH FDSDFLW\ EDODQFLQJ VWUDWHJ\ RI 6:00 UHGXFHV WKH RULJLQDOO\ H[FHVVLYH VWRUDJH FDSDFLW\ DQG PDNHV WKH GLVWULEXWLRQRIVWRUDJHFDSDFLW\PRUHXQLIRUPRQWKHZKROH $WWKH VDPHWLPHLW FDQ EH VHHQ IURPWKH SUHYLRXV VHWRI H[SHULPHQWVWKDWVXFKDEDODQFLQJVWUDWHJ\ZLOOQRWUHGXFH WKH,2EDQGZLGWKRIWKHDSSOLFDWLRQ

![](_page_4_Figure_1.png)

)LJXUH 6WRUDJHFDSDFLW\GLVWULEXWLRQVD7KHVWRUDJHFDSDFLW\ EHIRUHFDSDFLW\EDODQFLQJZLWK6:00 E7KHGLVWULEXWLRQRIVWRUDJH FDSDFLW\FKDQJHVXVLQJGHIDXOWFRQILJXUDWLRQ

#### 9 &21&/86,216

,Q RUGHU WR VROYH WKH WURXEOH IDFHG E\ WKH SHWDVFDOH VWRUDJH V\VWHP WKLV SDSHU SURSRVHG DQ ,2 PLGGOHZDUH EDVHG VROXWLRQ 7KH FRUH RI RXU PLGGOHZDUH LV 6:00 ZKLFK FDQ RSWLPL]H WKH ,2 SDWK ZKHQ PXOWLSOH DSSOLFDWLRQVDFFHVVWKHILOHV\VWHPDWWKHVDPHWLPHDQGVR LW FDQ LPSURYH WKH EDQGZLGWK HIILFLHQF\ 0HDQZKLOH D FDSDFLW\ EDODQFLQJ VWUDWHJ\ ZDV SXW IRUZDUGHG ZKLFK LV XVHG WR DGGUHVV WKH FDSDFLW\ XQEDODQFH SUREOHP LQ SHWDVFDOH VWRUDJHH[SDQVLRQ:HLPSOHPHQWHGRXUVROXWLRQ DQGWHVWHGLWRQWKH0LON\:D\$7+$VXSHUFRPSXWHU 7KH H[SHULPHQWDO UHVXOWV VKRZHG WKDW WKH ,2 SDWK RSWLPL]DWLRQDQGFDSDFLW\EDODQFLQJ VWUDWHJ\DFKLHYHGWKH GHVLUHG HIIHFW ,Q WKH IXWXUH ZH ZRXOG OLNH WR RSWLPL]H 6:00 VR DV WR SURYLGH VRPH KHOS IRU WKH VWRUDJH DUFKLWHFWXUHRIQH[WJHQHUDWLRQ V\VWHPV

#### $&.12:/('*0(17

7KLV ZRUN ZDV VXSSRUWHG E\ WKH 1DWLRQDO .H\ 5 ' 3URJUDPRI&KLQD12<)% DQG WKH16)& 12 :HWKDQN'U=KL-LH:DQJIRUKLVZDUP KHOSDQGVXJJHVWLRQV

#### 5()(5(1&(6

- >@ : ; ;X< 7 /X4 /L( 4 =KRX= / 6RQJ< 'RQJ: =KDQJ' 3 :HL ; 0 =KDQJ+ 7 &KHQ- < ;LQJ< <XDQ ³+\EULGKLHUDUFK\VWRUDJHV\VWHPLQ0LON\:D\VXSHUFRPSXWHU´ *Frontiers of Computer Science* YROQRSS
- >@ 520,2 $YDLODEOH RQOLQH KWWSVZZZPFVDQOJRYSURMHFWVURPLR $FFHVVHGRQ )HEUXDU\
- >@ 5 7KDNXU ( /XVN ³8VHUV JXLGH IRU URPLR D KLJKSHUIRUPDQFH SRUWDEOHPSLLRLPSOHPHQWDWLRQ´ 2IILFHRI6FLHQWLILF 7HFKQLFDO ,QIRUPDWLRQ 7HFKQLFDO 5HSRUWV $UJRQQH 1DWLRQDO /DERUDWRU\
- >@ *Lustre Software Release 2.x: Operations Manual.* ,QWHO&RUSRUDWLRQ &RS\ULJKW
- >@ *Slurm Workload Manager-Documentation* KWWSVVOXUPVFKHGPGFRPRYHUYLHZKWPO$FFHVVHGRQ )HEUXDU\
- >@ $ *HLVW 5 /XFDV ³0DMRU &RPSXWHU 6FLHQFH &KDOOHQJHV DW ([DVFDOH´ 6DJH3XEOLFDWLRQV,QF YROQR SS
- >@ : +X * 0 /LX 4 /L * / &DL ³6WRUDJH ZDOO IRU H[DVFDOH VXSHUFRPSXWLQJ´ *Frontiers of Information Technology & Electronic Engineering* YROQR SS
- >@ 7 *DR < 7 /X * 6XR ³8VLQJ0,& WR $FFHOHUDWH D 7\SLFDO 'DWD,QWHQVLYH $SSOLFDWLRQ 7KH %UHDGWKILUVW 6HDUFK´ ,Q *Proceedings of the 2013 IEEE 27th International Symposium on Parallel and Distributed Processing Workshops and PhD Forum* SS 0D\
- >@ < 7 /X+ 0DR 6KHQ³$'LVWULEXWHGILOHV\VWHPIUDPHZRUN IRU WUDQVSDUHQW DFFHVVLQJ KHWHURJHQHRXV VWRUDJH VHUYLFHV´ ,Q *Proceedings of the Parallel & Distributed Processing* SS 0D\
- >@ = * &KHQ< 7 /X1 ;LDR) /LX³$K\EULGPHPRU\EXLOWE\ VVGDQGGUDPWRVXSSRUWLQPHPRU\ELJGDWDDQDO\WLFV´ *Knowledge and Information Systems,* YRO QR SS
- >@ < 7 /X = < 6KHQ ( 4 =KRX0 =KX ³0FUP V\VWHP FLP EDVHGPXOWLSOHFOXVWHUVPDQDJHU´ *Neural Processing Letters* YRO QR SS
- >@ 0 ' 3KLOOLS/ -HUHP\³$KLJKSHUIRUPDQFHLPSOHPHQWDWLRQRI 03,,2 IRU D /XVWUH ILOH V\VWHP HQYLURQPHQW´ *Concurrency Compute. Pract. Exper,* YRO SS±
- >@ < 7 /X 1 ;LDR ; <DQJ ³6FDODEOH 5HVRXUFH0DQDJHPHQW 6\VWHP IRU +LJK 3URGXFWLYH &RPSXWLQJ´ ,Q *Proceedings of the Third ChinaGrid Annual Conference* $XJ
- >@ ( 4 =KRX< 7 /X1 ;LDR< 2X= * &KHQ; 4 %DR³$ WKHRUHWLFDODQDO\VLVRIOLIHVSDQLPSDFWRQIODVKPHPRU\LPSRVHGE\ HUDVXUH FRGH´ ,Q *Proceedings of the IEEE International Conference on Networking, Architecture and Storage*$XJ
- >@ % 'RQJ ; /L 4 :X / ;LDR / 5XDQ ³$ G\QDPLF DQG DGDSWLYHORDGEDODQFLQJVWUDWHJ\IRUSDUDOOHOILOHV\VWHPZLWKODUJH VFDOH ,2VHUYHUV´ *Journal of Parallel and distributed computing* YROQR SS
- >@ 0 .XQNHO³7RZDUGVDXWRPDWLFORDGEDODQFLQJRIDSDUDOOHOILOH V\VWHP ZLWK VXEILOH EDVHG PLJUDWLRQ´ 0DVWHU
V WKHVLV >2QOLQH@$YDLODEOH KWWSVDUFKLYXEXQLKHLGHOEHUJGHYROOWH[WVHUYHU
- >@ 0 ;LH< 7 /X/ /LX+ &DR; <DQJ³,PSOHPHQWDWLRQ DQG(YDOXDWLRQRI1HWZRUN,QWHUIDFHDQG0HVVDJH3DVVLQJ6HUYLFHV IRU7LDQ+H$6XSHUFRPSXWHU´ ,Q*Proceedings of the 19th Annual Symposium on High Performance Interconnects* $XJXVW
- >@ * 6XR< 7 /X; . /LDR0 ;LH+ &DR³1503,$1RQ VWRS DQG )DXOW 5HVLOLHQW 03,´ ,Q *Proceedings of the 2013 International Conference on Parallel and Distributed Systems* SS 'HFHPEHU

