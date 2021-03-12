from tkinter import *
import mysql.connector

database = mysql.connector.connect(host='localhost', port=3306, user='Eksamenssjef',
                                   passwd='oblig2019', db='oblig2019')

#Alternativ oppkobling:
#database = pymysql.connect(host='localhost', posrt=3306, user='Eksamenssjef',
                            #passwd='oblig2019', db='oblig2019')

def ajourholding():
    def ny_eksamen():
        def lagre_inndata():
            #Oppretter cursoren/markøren
            settinn_markor = database.cursor()

            #Bruker databasen
            emnekode = emnekode_inn.get()
            dato = dato_inn.get()
            romnr = romnr_inn.get()
        
            #if-test om en eksamen er registrert på samme dato og rom fra før
            sjekk_rom_markor = database.cursor()
            sjekk_rom_spørring=('''SELECT *
                                   FROM Eksamen
                                   WHERE Dato = %s
                                       AND Romnr = %s''')
            sjekk_rom_nydata=(dato, romnr)
            sjekk_rom_markor.execute(sjekk_rom_spørring, sjekk_rom_nydata)

            eksamen = 0
            for row in sjekk_rom_markor:
                eksamen = eksamen + 1
            sjekk_rom_markor.close()

            if eksamen == 0:
                settinn_eksamen=('''INSERT INTO Eksamen
                                    (Emnekode, Dato, Romnr)
                                    VALUES(%s, %s, %s)''')
                datany_eksamen=(emnekode, dato, romnr)
                settinn_markor.execute(settinn_eksamen, datany_eksamen)
                settinn_markor.close()
                database.commit()

                #Ny spørring for automatisk oppdatering av lista
                eksamen_markor = database.cursor()
                eksamen_markor.execute('''SELECT Emnekode, Dato, Romnr
                                          FROM Eksamen
                                          WHERE Dato >= NOW()
                                          ORDER BY Dato''')
                eksamener = []
                for row in eksamen_markor:
                    eksamener += [['Emnekode:', [row[0]], 'Dato:', [row[1]], 'Romnr:', [row[2]]]]
                eksamen_markor.close()

                innhold_eksamener.set(tuple(eksamener))
                info_ut.set('Eksamen registrert')
            else:
                info_ut.set('Eksamen ikke registrert')
                
        #------------------------------------------------------------------
        #lagre_inndata er ferdig definert
            
        registrer = Toplevel()
        registrer.title('Registrer ny eksamen')

        #Lager labels til inndatafeltene
        lbl_emnekode = Label(registrer, text='Oppgi emnekode:')
        lbl_emnekode.grid(row=0, column=0, padx=5, pady=5, sticky=E)

        lbl_dato = Label(registrer, text='Oppgi dato (YYYY-MM-DD):')
        lbl_dato.grid(row=1, column=0, padx=5, pady=5, sticky=E)

        lbl_romnr = Label(registrer, text='Oppgi romnr:')
        lbl_romnr.grid(row=2, column=0, padx=5, pady=5, sticky=E)

        #Lager inndatafelt
        emnekode_inn = StringVar()
        ent_emnekode = Entry(registrer, width=10, textvariable=emnekode_inn)
        ent_emnekode.grid(row=0, column=1, padx=5, pady=5, sticky=W)

        dato_inn = StringVar()
        ent_dato = Entry(registrer, width=15, textvariable=dato_inn)
        ent_dato.grid(row=1, column=1, padx=5, pady=5, sticky=W)

        romnr_inn = StringVar()
        ent_romnr = Entry(registrer, width=5, textvariable=romnr_inn)
        ent_romnr.grid(row=2, column=1, padx=5, pady=5, sticky=W)

        #Lager knapp for å lagre inndata som ny eksamen
        btn_lagre = Button(registrer, text='Lagre', command=lambda:[lagre_inndata(),registrer.destroy()])
        btn_lagre.grid(row=3, column=2, padx=5, pady=5, sticky=W)

        registrer.mainloop()
    #-----------------------------------------------------------------------------
    #ny_eksamen er ferdig definert
    def slett_eksamen():
        try:
            valgt = lst_eksamener.get(lst_eksamener.curselection())
            slett_fra_databasen = database.cursor()
            slette_markor=('''DELETE
                              FROM Eksamen
                              WHERE Emnekode = %s
                                  AND Dato = %s
                                  AND Romnr = %s''')
            spørringsdata=(valgt[1][0], valgt[3][0], valgt[5][0])
            slett_fra_databasen.execute(slette_markor, spørringsdata)
            slett_fra_databasen.close()
            database.commit()

            #Ny spørring for automatisk oppdatering av lista
            eksamen_markor = database.cursor()
            eksamen_markor.execute('''SELECT Emnekode, Dato, Romnr
                                      FROM Eksamen
                                      WHERE Dato >= NOW()
                                      ORDER BY Dato''')
            eksamener = []
            for row in eksamen_markor:
                eksamener += [['Emnekode:', [row[0]], 'Dato:', [row[1]], 'Romnr:', [row[2]]]]
            innhold_eksamener.set(tuple(eksamener))
            eksamen_markor.close()
            info_ut.set('Eksamen slettet')
        except:
            info_ut.set('Eksamen kan ikke slettes')
        
    #-------------------------------------------------------------------
    #slett_eksamen er ferdig definert
        
    eksamen_markor = database.cursor()
    eksamen_markor.execute('''SELECT Emnekode, Dato, Romnr
                              FROM Eksamen
                              WHERE Dato >= NOW()
                              ORDER BY Dato''')
    eksamener = []
    for row in eksamen_markor:
        eksamener += [['Emnekode:', [row[0]], 'Dato:', [row[1]], 'Romnr:', [row[2]]]]
    eksamen_markor.close()

    eksamenoversikt = Toplevel()
    eksamenoversikt.title('Eksamenoversikt')

    #Listebox og Scrollbar
    y_scroll = Scrollbar(eksamenoversikt, orient=VERTICAL)
    y_scroll.grid(row=1, column=1, rowspan=5, padx=(0,25), pady=5, sticky=NS)

    innhold_eksamener = StringVar()
    lst_eksamener = Listbox(eksamenoversikt, width=55, height=10, listvariable=innhold_eksamener, yscrollcommand=y_scroll.set)
    lst_eksamener.grid(row=1, column=0, rowspan=5, padx=(25,0), pady=5, sticky=E)
    innhold_eksamener.set(tuple(eksamener))
    y_scroll['command']=lst_eksamener.yview

    #Utdatafelt med informasjon til brukeren
    info_ut = StringVar()
    ent_info_ut = Entry(eksamenoversikt, width=30, state='readonly', textvariable=info_ut)
    ent_info_ut.grid(row=6, column=0, columnspan=3, padx=25, pady=5, sticky=W)

    #Knapp for å slette en eksamen
    btn_slett_eksamen = Button(eksamenoversikt, text='Slett valgt eksamen', command=slett_eksamen)
    btn_slett_eksamen.grid(row=2, column=3, columnspan=2, padx=5, pady=5, sticky=W)

    #Knapp for å legge til en ny eksamen
    btn_ny_eksamen = Button(eksamenoversikt, text='Registrer ny eksamen', command=ny_eksamen)
    btn_ny_eksamen.grid(row=1, column=3, columnspan=2, padx=5, pady=5, sticky=W)

    #Knapp for å lukke vindeut
    btn_lukk_vindu = Button(eksamenoversikt, text='Lukk vindu', command=eksamenoversikt.destroy)
    btn_lukk_vindu.grid(row=6, column=4, padx=5, pady=5, sticky=W)

    eksamenoversikt.mainloop()

def etter_dato():
    def spesifik_dato():
        def finn_eksamen_spesifik():
            #Markør for å finne eksamener
            søk_markor = database.cursor()
            spesdato = spesdato_inn.get()
            søk_eksamen=('''SELECT Emnekode, Dato, Romnr
                            FROM Eksamen
                            WHERE Dato = %s''')
            datany_eksamen=(spesdato,)
            søk_markor.execute(søk_eksamen, datany_eksamen)

            eksamener = []
            for row in søk_markor:
                eksamener += [['Emnekode:', [row[0]], 'Dato:', [row[1]], 'Romnr:', [row[2]]]]
            søk_markor.close()

            innhold_eksamen.set(tuple(eksamener))

    #-----------------------------------------------------------------------
    #finn_eksamen er ferdig definert

        spesifik = Toplevel()
        spesifik.title('Spesifik Dato')

        #Label for inndataen til datoen
        lbl_spesdato_inn = Label(spesifik, text='Oppgi dato (YYYY-MM-DD):')
        lbl_spesdato_inn.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=E)

        #Inndatafelt for dato
        spesdato_inn = StringVar()
        ent_spesdato_inn = Entry(spesifik, width=15, textvariable=spesdato_inn)
        ent_spesdato_inn.grid(row=0, column=2, padx=5, pady=5, sticky=W)

        #Knapp for å søke
        btn_søk = Button(spesifik, text='Søk', width=10, command=finn_eksamen_spesifik)
        btn_søk.grid(row=0, column=3, padx=5, pady=5, sticky=W)

        y_scroll = Scrollbar(spesifik, orient=VERTICAL)
        y_scroll.grid(row=1, column=3, rowspan=5, padx=(0,25), pady=5, sticky=NS+W)

        innhold_eksamen = StringVar()
        lst_eksamen = Listbox(spesifik, width=50, height=10, listvariable=innhold_eksamen, yscrollcommand=y_scroll.set)
        lst_eksamen.grid(row=1, column=0, columnspan=3, rowspan=5, padx=(25,0), pady=5, sticky=E)
        y_scroll['command']=lst_eksamen.yview

        #Knapp for å lukke vinduet
        btn_lukk_vindu = Button(spesifik, text='Lukk vindu', command=spesifik.destroy)
        btn_lukk_vindu.grid(row=6, column=4, padx=5, pady=5, sticky=E)

        spesifik.mainloop()
    def periode_dato():
        def finn_eksamen_periode():
            #Markør for å finne eksamener
            søk_markor = database.cursor()
            fra_periode = fra_periode_inn.get()
            til_periode = til_periode_inn.get()
            søk_eksamen=('''SELECT Emnekode, Dato, Romnr
                            FROM Eksamen
                            WHERE Dato >= %s
                                AND Dato <= %s
                            ORDER BY Dato''')
            datany_eksamen=(fra_periode, til_periode)
            søk_markor.execute(søk_eksamen, datany_eksamen)

            eksamener = []
            for row in søk_markor:
                eksamener += [['Emnekode:', [row[0]], 'Dato:', [row[1]], 'Romnr:', [row[2]]]]
            søk_markor.close()

            innhold_eksamen.set(tuple(eksamener))
        #------------------------------------------------------------------------------
        #finn_eksamen_periode ferdig definert
            
        periode = Toplevel()
        periode.title('Periode Dato')

        #Labels for inndataene
        lbl_informasjon = Label(periode, text='Datoer skrives i format (YYYY-MM-DD)')
        lbl_informasjon.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky=E)

        lbl_fra_periode = Label(periode, text='Oppgi "fra" dato:')
        lbl_fra_periode.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=E)

        lbl_til_periode = Label(periode, text='Oppgi "til" dato:')
        lbl_til_periode.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=E)

        #Inndatafelt for datoene
        fra_periode_inn = StringVar()
        ent_fra_periode_inn = Entry(periode, width=15, textvariable=fra_periode_inn)
        ent_fra_periode_inn.grid(row=1, column=2, padx=5, pady=5, sticky=W)

        til_periode_inn = StringVar()
        ent_til_periode_inn = Entry(periode, width=15, textvariable=til_periode_inn)
        ent_til_periode_inn.grid(row=2, column=2, padx=5, pady=5, sticky=W)

        #Knapp for å søke
        btn_søk = Button(periode, text='Søk', width=10, command=finn_eksamen_periode)
        btn_søk.grid(row=2, column=3, padx=5, pady=5, sticky=W)

        #Listebox og scrollbar som skal inneholde informasjon
        y_scroll = Scrollbar(periode, orient=VERTICAL)
        y_scroll.grid(row=3, column=5, rowspan=5, padx=(0,25), pady=5, sticky=NS+W)

        innhold_eksamen = StringVar()
        lst_eksamen = Listbox(periode, width=50, listvariable=innhold_eksamen, yscrollcomman=y_scroll.set)
        lst_eksamen.grid(row=3, column=0, columnspan=5, rowspan=5, padx=(25,0), pady=5, sticky=E)
        y_scroll['command']=lst_eksamen.yview

        #Knapp for å lukke vinduet
        btn_lukk_vindu = Button(periode, text='Lukk vindu', command=periode.destroy)
        btn_lukk_vindu.grid(row=8, column=5, columnspan=2, padx=5, pady=5, sticky=E)

        periode.mainloop()

    #--------------------------------------------------------------------------------
    #periode_dato ferdig definert

    datomeny = Toplevel()
    datomeny.title('Dato Meny')

    #Labels til undermenyen
    lbl_spesifik_dato = Label(datomeny, text='Søk på eksamen etter spesifik dato:')
    lbl_spesifik_dato.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky=E)

    lbl_periode_dato = Label(datomeny, text='Søk på eksammen inne i en periode:')
    lbl_periode_dato.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky=E)

    #Buttons til undermenyen
    btn_spesifik_dato = Button(datomeny, text='Spesifik', command=spesifik_dato)
    btn_spesifik_dato.grid(row=0, column=3, columnspan=2, padx=5, pady=5, sticky=W)

    btn_periode_dato = Button(datomeny, text='Periode', command=periode_dato)
    btn_periode_dato.grid(row=1, column=3, columnspan=2, padx=5, pady=5, sticky=W)

    #Button for å lukke vinduet
    btn_lukk = Button(datomeny, text='Lukk vindu', command=datomeny.destroy)
    btn_lukk.grid(row=3, column=3, columnspan=2, padx=5, pady=5, sticky=W)

    datomeny.mainloop()

def karakterlisteGUI():
    def finn_karakterer():
        søk_markor = database.cursor()
        emnekode = emnekode_inn.get()
        søk_eksamen=('''SELECT Studentnr, Karakter
                        FROM Eksamensresultat
                        WHERE Emnekode = %s
                            AND Karakter IS NOT NULL
                        ORDER BY Studentnr''')
        datany_eksamen=(emnekode,)
        søk_markor.execute(søk_eksamen, datany_eksamen)

        eksamener = []
        for row in søk_markor:
            eksamener += [['Studentnr:', [row[0]], 'Karakter:', [row[1]]]]
        søk_markor.close()

        innhold_eksamen.set(tuple(eksamener))

    #------------------------------------------------------------------------------
    #finn_karakterer ferdig definert
    
    karakterliste = Toplevel()
    karakterliste.title('Karakterliste')

    #Label til inndatafeltet
    lbl_emnekode = Label(karakterliste, text='Oppgi emnekode:')
    lbl_emnekode.grid(row=0, column=0, padx=5, pady=5, sticky=E)

    #Inndatafelt for emnekode
    emnekode_inn = StringVar()
    ent_emnekode_inn = Entry(karakterliste, width=10, textvariable=emnekode_inn)
    ent_emnekode_inn.grid(row=0, column=1, padx=5, pady=5, sticky=W)

    btn_emnekode = Button(karakterliste, width=10, text='Søk', command=finn_karakterer)
    btn_emnekode.grid(row=0, column=2, padx=5, pady=5, sticky=W)

    y_scroll = Scrollbar(karakterliste, orient=VERTICAL)
    y_scroll.grid(row=3, column=3, rowspan=5, padx=(0,25), pady=5, sticky=NS)

    innhold_eksamen = StringVar()
    lst_eksamen = Listbox(karakterliste, width=35, height=10, listvariable=innhold_eksamen, yscrollcommand=y_scroll.set)
    lst_eksamen.grid(row=3, column=0, columnspan=3, rowspan=5, padx=(25,0), pady=5, sticky=E)
    y_scroll['command']=lst_eksamen.yview

    #Knapp for å lukke vinduet
    btn_lukk_vindu = Button(karakterliste, text='Lukk vindu', command=karakterliste.destroy)
    btn_lukk_vindu.grid(row=8, column=4, padx=5, pady=5, sticky=W)

    karakterliste.mainloop()
    

def registrer_karakterGUI():
    def hent_studenter():
        karakter_ut.set('')
        innhold_dato.set('')
        innhold_studenter.set('')

        søk_dato_markor = database.cursor()
        emnekode = emnekode_inn.get()
        dato_spørring=('''SELECT Dato
                          FROM Eksamen
                          WHERE Emnekode = %s
                              AND Dato <= NOW()''')
        nydata_spørring=(emnekode,)
        søk_dato_markor.execute(dato_spørring, nydata_spørring)

        datoer = []
        for row in søk_dato_markor:
            datoer += [row]
        innhold_dato.set(tuple(datoer))

    #--------------------------------------------------------------------------
    #hent_studenter ferdig definert

    def student_klikk(event):
        #Søker etter karakter for studentene på valgt emne
        if lst_studenter.curselection() != ():
            karakter_ut.set('')
            studentnr = lst_studenter.get(lst_studenter.curselection())
            karakter_markor = database.cursor()
            emnekode = emnekode_inn.get()
            #dato = lst_datoer.get(lst_datoer.curselection())
            karakter_spørring=('''SELECT Studentnr, Karakter, Dato
                                  FROM Eksamensresultat
                                  WHERE Studentnr = %s
                                      AND Emnekode = %s
                                      AND Dato = %s''')
            nydata_spørring=(studentnr[0], emnekode, dato[0])
            karakter_markor.execute(karakter_spørring, nydata_spørring)

            for row in karakter_markor:
                if studentnr[0]==row[0]:
                    karakter_ut.set(row[1])
            karakter_markor.close()
            studentnr_ut.set(studentnr[0])

    #--------------------------------------------------------------------------
    #student_klikk ferdig definert

    def registrer_karakter():
        studentnr = lst_studenter.get(lst_studenter.curselection())
        emnekode = emnekode_inn.get()
        registrer_markor = database.cursor()
        karakter = registrer_karakter_inn.get()
        karakter_sjekk = karakter_ut.get()
        if karakter_sjekk == '':
            registrerings_spørring=('''INSERT INTO Eksamensresultat
                                       (Studentnr, Emnekode, Dato, Karakter)
                                       VALUES(%s, %s, %s, %s)''')
            nydata_spørring=(studentnr[0], emnekode, dato[0], karakter)
            registrer_markor.execute(registrerings_spørring, nydata_spørring)
            registrer_markor.close()
            database.commit()
        else:
            registrerings_spørring=('''UPDATE Eksamensresultat
                                       SET Karakter = %s
                                       WHERE Studentnr = %s
                                           AND Emnekode = %s
                                           AND Dato = %s''')
            nydata_spørring=(karakter, studentnr[0], emnekode, dato[0])
            registrer_markor.execute(registrerings_spørring, nydata_spørring)
            registrer_markor.close()
            database.commit()

        karakter_markor = database.cursor()
        karakter_spørring=('''SELECT Studentnr, Karakter, Dato
                              FROM Eksamensresultat
                              WHERE Studentnr = %s
                                  AND Emnekode = %s
                                  AND Dato = %s''')
        nydata_spørring=(studentnr[0], emnekode, dato[0])
        karakter_markor.execute(karakter_spørring, nydata_spørring)

        for row in karakter_markor:
            if studentnr[0]==row[0]:
                karakter_ut.set(row[1])
        karakter_markor.close()
        registrer_karakter_inn.set('')

    #--------------------------------------------------------------------------
    #registrer_karakter ferdig definert

    def dato_klikk(event):
        if lst_datoer.curselection() != ():
            karakter_ut.set('')
            global dato
            dato = lst_datoer.get(lst_datoer.curselection())

            #Søker etter studentnummer
            søk_student_markor = database.cursor()
            søk_student_markor.execute('''SELECT Studentnr, Fornavn, Etternavn
                                          FROM Student''')
            studenter = []
            for row in søk_student_markor:
                studenter += [row]
            søk_student_markor.close()
            innhold_studenter.set(tuple(studenter))
            dato_ut.set(dato)

    #--------------------------------------------------------------------------
    #dato_klikk er ferdig definert
            
    regkar = Toplevel()
    regkar.title('Registrer karakterer')

    #Label for inndata av emnekode
    lbl_emnekode_inn = Label(regkar, text='Tast inn emnekoden for eksamen du ønsker å registrere karakterer i:')
    lbl_emnekode_inn.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky=E)

    lbl_karakter_ut = Label(regkar, text='Registrert karakter:')
    lbl_karakter_ut.grid(row=3, column=5, padx=5, pady=5, sticky=E)

    lbl_registrer_karakter = Label(regkar, text='Registrer karakter:')
    lbl_registrer_karakter.grid(row=1, column=5, padx=5, pady=5, sticky=E)

    lbl_dato_ut = Label(regkar, text='Dato:')
    lbl_dato_ut.grid(row=5, column=5, padx=5, pady=5, sticky=E)

    lbl_studentnr_ut = Label(regkar, text='Studentnr:')
    lbl_studentnr_ut.grid(row=4, column=5, padx=5, pady=5, sticky=E)

    lbl_velg_dato = Label(regkar, text='Velg dato:')
    lbl_velg_dato.grid(row=1, column=0, padx=25, pady=5, sticky=SW)

    lbl_velg_student = Label(regkar, text='Velg student:')
    lbl_velg_student.grid(row=1, column=3, padx=25, pady=5, sticky=SW)

    #Inndata for emnekode og registrering av karakter
    emnekode_inn = StringVar()
    ent_emnekode_inn = Entry(regkar, width=10, textvariable=emnekode_inn)
    ent_emnekode_inn.grid(row=0, column=5, padx=5, pady=5, sticky=W)

    registrer_karakter_inn = StringVar()
    ent_registrer_karakter_inn = Entry(regkar, width=5, textvariable=registrer_karakter_inn)
    ent_registrer_karakter_inn.grid(row=1, column=6, padx=5, pady=5, sticky=W)

    #Button for å søke etter studenter og registrere karakterer
    btn_søk = Button(regkar, width=10, text='Søk', command=hent_studenter)
    btn_søk.grid(row=0, column=6, padx=5, pady=5, sticky=W)

    btn_registrer_karakter_inn = Button(regkar, width=10, text='Registrer', command=registrer_karakter)
    btn_registrer_karakter_inn.grid(row=2, column=6, padx=5, pady=5, sticky=W)

    #Listebox med scrollbar som viser studentnummer og datoer
    y_scroll_studentnr = Scrollbar(regkar, orient=VERTICAL)
    y_scroll_studentnr.grid(row=2, column=4, rowspan=5, padx=(0,25), pady=5, sticky=NS)

    y_scroll_dato = Scrollbar(regkar, orient=VERTICAL)
    y_scroll_dato.grid(row=2, column=1, rowspan=5, padx=(0,25), pady=5, sticky=NS)

    #Utdatafelt
    karakter_ut = StringVar()
    ent_karakter_ut = Entry(regkar, width=5, state='readonly', textvariable=karakter_ut)
    ent_karakter_ut.grid(row=3, column=6, padx=5, pady=5, sticky=W)

    dato_ut = StringVar()
    ent_dato_ut = Entry(regkar, width=15, state='readonly', textvariable=dato_ut)
    ent_dato_ut.grid(row=5, column=6, padx=5, pady=5, sticky=W)

    studentnr_ut = StringVar()
    ent_studentnr_ut = Entry(regkar, width=15, state='readonly', textvariable=studentnr_ut)
    ent_studentnr_ut.grid(row=4, column=6, padx=5, pady=5, sticky=W)

    #Lisetbox med studentnummer
    innhold_studenter = StringVar()
    lst_studenter = Listbox(regkar, width=25, height=10, listvariable=innhold_studenter, yscrollcommand=y_scroll_studentnr.set)
    lst_studenter.grid(row=2, column=3, rowspan=5, padx=(25,0), pady=5, sticky=E)
    y_scroll_studentnr['command']=lst_studenter.yview
    lst_studenter.bind('<<ListboxSelect>>', student_klikk)

    #Listebox med datoer
    innhold_dato = StringVar()
    lst_datoer = Listbox(regkar, width=25, height=10, listvariable=innhold_dato, yscrollcommand=y_scroll_dato.set)
    lst_datoer.grid(row=2, column=0, rowspan=5, padx=(25,0), pady=5, sticky=E)
    y_scroll_dato['command']=lst_datoer.yview
    lst_datoer.bind('<<ListboxSelect>>', dato_klikk)

    #Knapp for å lukke vinduet
    btn_lukk_vindu = Button(regkar, text='Lukk vindu', command=regkar.destroy)
    btn_lukk_vindu.grid(row=6, column=6, padx=5, pady=5, sticky=W)

    regkar.mainloop()

def karakterfordelingGUI():
    def hent_datoer():
        innhold_dato.set('')
        emnenavn_ut.set('')
        karakter_a_ut.set('')
        karakter_b_ut.set('')
        karakter_c_ut.set('')
        karakter_d_ut.set('')
        karakter_e_ut.set('')
        karakter_f_ut.set('')
        ikke_møtt_ut.set('')
        søk_dato_markor = database.cursor()
        emnekode = emnekode_inn.get()
        dato_spørring=('''SELECT Dato
                          FROM Eksamen
                          WHERE Emnekode = %s
                              AND Dato <= NOW()''')
        nydata_spørring=(emnekode,)
        søk_dato_markor.execute(dato_spørring, nydata_spørring)

        datoer = []
        for row in søk_dato_markor:
            datoer += [row]
        innhold_dato.set(tuple(datoer))
        
    #-------------------------------------------------------------------
    #hent_datoer ferdig definert

    def dato_klikk(event):
        if lst_datoer.curselection() != ():
            dato = dato = lst_datoer.get(lst_datoer.curselection())
            emnekode = emnekode_inn.get()

            søk_emnenavn_markor = database.cursor()
            emnenavn_spørring=('''SELECT Emnenavn
                                  FROM Emne
                                  WHERE Emnekode = %s''')
            emnenavn_data=(emnekode,)
            søk_emnenavn_markor.execute(emnenavn_spørring, emnenavn_data)

            emnenavn = []
            for row in søk_emnenavn_markor:
                emnenavn += [row[0]]
            søk_emnenavn_markor.close()

            emnenavn_ut.set(emnenavn[0])

            søk_karakterer = database.cursor()
            karakterer_spørring=('''SELECT Karakter
                                    FROM Eksamensresultat
                                    WHERE Dato = %s
                                        AND Emnekode = %s
                                    ORDER BY Karakter''')
            karakterer_data=(dato[0], emnekode)
            søk_karakterer.execute(karakterer_spørring, karakterer_data)

            karakter_a = 0
            karakter_b = 0
            karakter_c = 0
            karakter_d = 0
            karakter_e = 0
            karakter_f = 0
            ikke_møtt = 0
            for row in søk_karakterer:
                if row[0] == 'A' or row[0] == 'a':
                    karakter_a = karakter_a + 1
                elif row[0] == 'B' or row[0] == 'b':
                    karakter_b = karakter_b + 1
                elif row[0] == 'C' or row[0] == 'c':
                    karakter_c = karakter_c + 1
                elif row[0] == 'D' or row[0] == 'd':
                    karakter_d = karakter_d + 1
                elif row[0] == 'E' or row[0] == 'e':
                    karakter_e = karakter_e + 1
                elif row[0] == 'F' or row[0] == 'f':
                    karakter_f = karakter_f + 1
                else:
                    ikke_møtt = ikke_møtt + 1

            karakter_a_ut.set(karakter_a)
            karakter_b_ut.set(karakter_b)
            karakter_c_ut.set(karakter_c)
            karakter_d_ut.set(karakter_d)
            karakter_e_ut.set(karakter_e)
            karakter_f_ut.set(karakter_f)
            ikke_møtt_ut.set(ikke_møtt)
            søk_karakterer.close()
                

    #--------------------------------------------------------------------
    #dato_klikk ferdig definert
        
    karakterfordeling=Toplevel()
    karakterfordeling.title('Karakterfordeling')

    #Labels for inndata
    #lbl_emnekode_inn = Label(karakterfordeling, text='Tast inn emnekoden for eksamen du ønsker å se karakterstatistikken for:')
    lbl_emnekode_inn = Label(karakterfordeling, text='Oppgi emnekode:')
    lbl_emnekode_inn.grid(row=0, column=0, padx=5, pady=5, sticky=E)

    #Labels for karakterene
    lbl_karakter_a = Label(karakterfordeling, text='A:')
    lbl_karakter_a.grid(row=2, column=3, padx=5, pady=5, sticky=E)

    lbl_karakter_b = Label(karakterfordeling, text='B:')
    lbl_karakter_b.grid(row=3, column=3, padx=5, pady=5, sticky=E)

    lbl_karakter_c = Label(karakterfordeling, text='C:')
    lbl_karakter_c.grid(row=4, column=3, padx=5, pady=5, sticky=E)

    lbl_karakter_d = Label(karakterfordeling, text='D:')
    lbl_karakter_d.grid(row=5, column=3, padx=5, pady=5, sticky=E)

    lbl_karakter_e = Label(karakterfordeling, text='E:')
    lbl_karakter_e.grid(row=6, column=3, padx=5, pady=5, sticky=E)

    lbl_karakter_f = Label(karakterfordeling, text='F:')
    lbl_karakter_f.grid(row=7, column=3, padx=5, pady=5, sticky=E)

    lbl_ikke_møtt = Label(karakterfordeling, text='Ikke møtt:')
    lbl_ikke_møtt.grid(row=8, column=3, padx=5, pady=5, sticky=E)

    lbl_velg_dato = Label(karakterfordeling, text='Velg Dato:')
    lbl_velg_dato.grid(row=1, column=0, padx=10, pady=5, sticky=S)

    #Inndatafelt
    emnekode_inn = StringVar()
    ent_emnekode_inn = Entry(karakterfordeling, width=10, textvariable=emnekode_inn)
    ent_emnekode_inn.grid(row=0, column=1, padx=5, pady=5, sticky=W)

    #Utdatafelt
    emnenavn_ut = StringVar()
    ent_emnenavn_ut = Entry(karakterfordeling, width=35, state='readonly', textvariable=emnenavn_ut)
    ent_emnenavn_ut.grid(row=1, column=2, columnspan=3, padx=5, pady=5, sticky=W)

    karakter_a_ut = StringVar()
    ent_karakter_a = Entry(karakterfordeling, width=5, state='readonly', textvariable=karakter_a_ut)
    ent_karakter_a.grid(row=2, column=4, padx=5, pady=5, sticky=W)

    karakter_b_ut = StringVar()
    ent_karakter_b = Entry(karakterfordeling, width=5, state='readonly', textvariable=karakter_b_ut)
    ent_karakter_b.grid(row=3, column=4, padx=5, pady=5, sticky=W)

    karakter_c_ut = StringVar()
    ent_karakter_c = Entry(karakterfordeling, width=5, state='readonly', textvariable=karakter_c_ut)
    ent_karakter_c.grid(row=4, column=4, padx=5, pady=5, sticky=W)

    karakter_d_ut = StringVar()
    ent_karakter_d = Entry(karakterfordeling, width=5, state='readonly', textvariable=karakter_d_ut)
    ent_karakter_d.grid(row=5, column=4, padx=5, pady=5, sticky=W)

    karakter_e_ut = StringVar()
    ent_karakter_e = Entry(karakterfordeling, width=5, state='readonly', textvariable=karakter_e_ut)
    ent_karakter_e.grid(row=6, column=4, padx=5, pady=5, sticky=W)

    karakter_f_ut = StringVar()
    ent_karakter_f = Entry(karakterfordeling, width=5, state='readonly', textvariable=karakter_f_ut)
    ent_karakter_f.grid(row=7, column=4, padx=5, pady=5, sticky=W)

    ikke_møtt_ut = StringVar()
    ent_ikke_møtt = Entry(karakterfordeling, width=5, state='readonly', textvariable=ikke_møtt_ut)
    ent_ikke_møtt.grid(row=8, column=4, padx=5, pady=5, sticky=W)

    #Buttons
    btn_søk = Button(karakterfordeling, width=10, text='Søk', command=hent_datoer)
    btn_søk.grid(row=0, column=2, padx=5, pady=5, sticky=W)

    #Listebox og scrollbar
    y_scroll = Scrollbar(karakterfordeling, orient=VERTICAL)
    y_scroll.grid(row=2, column=1, rowspan=5, padx=(0,25), pady=5, sticky=NS+W)
    
    innhold_dato = StringVar()
    lst_datoer = Listbox(karakterfordeling, width=15, height=10, listvariable=innhold_dato, yscrollcommand=y_scroll.set)
    lst_datoer.grid(row=2, column=0, rowspan=5, padx=(25,0), pady=5, sticky=E)
    y_scroll['command']=lst_datoer.yview
    lst_datoer.bind('<<ListboxSelect>>', dato_klikk)

    #Knapp for å lukke vinduet
    btn_lukk_vindu = Button(karakterfordeling, text='Lukk vindu', command=karakterfordeling.destroy)
    btn_lukk_vindu.grid(row=9, column=4, padx=5, pady=5, sticky=W)

    karakterfordeling.mainloop()


def eksamensresultaterGUI():
    def søk_knapp():
        innhold_karakterer.set('')
        fornavn_ut.set('')
        etternavn_ut.set('')

        studentnr = studentnr_inn.get()

        finn_navn_markor = database.cursor()
        finn_navn_spørring=('''SELECT Fornavn, Etternavn
                               FROM Student
                               WHERE Studentnr = %s''')
        finn_navn_nydata=(studentnr,)
        finn_navn_markor.execute(finn_navn_spørring, finn_navn_nydata)

        for row in finn_navn_markor:
            fornavn_ut.set([row[0]])
            etternavn_ut.set([row[1]])
        
        søk_karakterer = database.cursor()
        søk_karakterer_spørring=('''SELECT Karakter, Studiepoeng, Emnenavn, Dato 
                                    FROM Emne, Eksamensresultat
                                    WHERE Studentnr = %s
                                        AND Emne.Emnekode = Eksamensresultat.Emnekode
                                    ORDER BY Dato''')
        søk_karakterer_nydata=(studentnr,)
        søk_karakterer.execute(søk_karakterer_spørring, søk_karakterer_nydata)

        
        utdata_ut = []
        for row in søk_karakterer:
            karakter_ut = []
            studiepoeng_ut = []
            emnenavn_ut = []
            dato_ut = []
            karakter_ut += [row[0]]
            if row[0] == 'F' or row[0] == 'f':
                studiepoeng_ut += '0'
            else:
                studiepoeng_ut += [row[1]]
            emnenavn_ut += [row[2]]
            dato_ut += [row[3]]

            utdata_ut += [[karakter_ut[0], emnenavn_ut[0], studiepoeng_ut[0], dato_ut[0]]]
         
        innhold_karakterer.set(tuple(utdata_ut))
        søk_karakterer.close()

    #---------------------------------------------------------------------
    #søk_knapp ferdig definert

        
    eksamensresultater = Toplevel()
    eksamensresultater.title('Eksamensresultater')

    #Labels
    lbl_studentnr = Label(eksamensresultater, text='Oppgi studentnr:')
    lbl_studentnr.grid(row=0, column=0, padx=5, pady=5, sticky=E)

    lbl_fornavn = Label(eksamensresultater, text='Fornavn:')
    lbl_fornavn.grid(row=1, column=0, padx=5, pady=5, sticky=E)

    lbl_etternavn = Label(eksamensresultater, text='Etternavn:')
    lbl_etternavn.grid(row=1, column=2, padx=5, pady=5, sticky=E)

    #Inndatafelt
    studentnr_inn = StringVar()
    ent_studentnr_inn = Entry(eksamensresultater, width=10, textvariable=studentnr_inn)
    ent_studentnr_inn.grid(row=0, column=1, padx=5, pady=5, sticky=W)

    #Utdatafelt
    fornavn_ut = StringVar()
    ent_fornavn_ut = Entry(eksamensresultater, width=15, state='readonly', textvariable=fornavn_ut)
    ent_fornavn_ut.grid(row=1, column=1, padx=5, pady=5, sticky=W)

    etternavn_ut = StringVar()
    ent_etternavn_ut = Entry(eksamensresultater, width=15, state='readonly', textvariable=etternavn_ut)
    ent_etternavn_ut.grid(row=1, column=3, padx=5, pady=5, sticky=W)

    #Buttons
    btn_søk = Button(eksamensresultater, width=10, text='Søk', command=søk_knapp)
    btn_søk.grid(row=0, column=2, padx=5, pady=5, sticky=W)

    #Listebox og Scrollbar
    y_scroll = Scrollbar(eksamensresultater, orient=VERTICAL)
    y_scroll.grid(row=2, column=3, rowspan=5, padx=(0,25), pady=15, sticky=NS+W)

    innhold_karakterer = StringVar()
    lst_karakterer = Listbox(eksamensresultater, width=50, height=10, listvariable=innhold_karakterer, yscrollcommand=y_scroll.set)
    lst_karakterer.grid(row=2, column=0, columnspan=3, rowspan=5, padx=(25,0), pady=15, sticky=E)
    y_scroll['command']=lst_karakterer.yview

    #Knapp for å lukke vinduet
    btn_lukk_vindu = Button(eksamensresultater, text='Lukk vindu', command=eksamensresultater.destroy)
    btn_lukk_vindu.grid(row=7, column=3, padx=5, pady=5, sticky=W)

    eksamensresultater.mainloop()


def vitnemålGUI():
    def søk_knapp():
        fornavn_ut.set('')
        etternavn_ut.set('')
        innhold_karakterer.set('')
        studentnr = studentnr_inn.get()

        finn_navn_markor = database.cursor()
        finn_navn_spørring=('''SELECT Fornavn, Etternavn
                               FROM Student
                               WHERE Studentnr = %s''')
        finn_navn_nydata=(studentnr,)
        finn_navn_markor.execute(finn_navn_spørring, finn_navn_nydata)

        for row in finn_navn_markor:
            fornavn_ut.set([row[0]])
            etternavn_ut.set([row[1]])

        finn_vitnemål_markor = database.cursor()
        finn_vitnemål_spørring=('''SELECT Emne.Emnekode, Emnenavn, Dato, MIN(Karakter), Studiepoeng
                                   FROM Emne, Eksamensresultat
                                   WHERE Studentnr = %s
                                       AND Emne.Emnekode = Eksamensresultat.Emnekode
                                    GROUP BY Emnekode
                                    ORDER BY RIGHT(Emne.Emnekode,4)''')
        finn_vitnemål_nydata=(studentnr,)
        finn_vitnemål_markor.execute(finn_vitnemål_spørring, finn_vitnemål_nydata)

        karakterer = []
        antall_studiepoeng = 0
        
        for row in finn_vitnemål_markor:
            karakterer += [row]
            antall_studiepoeng += row[4]

        innhold_karakterer.set(tuple(karakterer))
        studiepoeng_ut.set(antall_studiepoeng)
        finn_vitnemål_markor.close()
    #------------------------------------------------------------------------
    #søk_knapp ferdig definert

        
    vitnemål = Toplevel()
    vitnemål.title('Vitnemål')

    #Labels
    lbl_studentnr_inn = Label(vitnemål, text='Oppgi studentnr:')
    lbl_studentnr_inn.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=E)

    lbl_fornavn_ut = Label(vitnemål, text='Fornavn:')
    lbl_fornavn_ut.grid(row=1, column=0, padx=5, pady=5, sticky=E)

    lbl_etternavn_ut = Label(vitnemål, text='Etternavn:')
    lbl_etternavn_ut.grid(row=1, column=2, padx=5, pady=5, sticky=E)

    lbl_studiepoeng = Label(vitnemål, text='Studiepoeng:')
    lbl_studiepoeng.grid(row=7, column=0, padx=5, pady=5, sticky=E)

    #Inndata
    studentnr_inn = StringVar()
    ent_studentnr_inn = Entry(vitnemål, width=10, textvariable=studentnr_inn)
    ent_studentnr_inn.grid(row=0, column=2, padx=5, pady=5, sticky=W)

    #Utdata
    fornavn_ut = StringVar()
    ent_fornavn_ut = Entry(vitnemål, width=15, state='readonly', textvariable=fornavn_ut)
    ent_fornavn_ut.grid(row=1, column=1, padx=5, pady=5, sticky=W)

    etternavn_ut = StringVar()
    ent_etternavn_ut = Entry(vitnemål, width=15, state='readonly', textvariable=etternavn_ut)
    ent_etternavn_ut.grid(row=1, column=3, padx=5, pady=5, sticky=W)

    studiepoeng_ut = StringVar()
    ent_studiepoeng_ut = Entry(vitnemål, width=5, state='readonly', textvariable=studiepoeng_ut)
    ent_studiepoeng_ut.grid(row=7, column=1, padx=5, pady=5, sticky=W)

    #Buttons
    btn_søk = Button(vitnemål, text='Søk', width=10, command=søk_knapp)
    btn_søk.grid(row=0, column=3, padx=5, pady=5, sticky=W)

    #Listbox og scrollbar
    y_scroll = Scrollbar(vitnemål, orient=VERTICAL)
    y_scroll.grid(row=2, column=5, rowspan=5, padx=(0,25), pady=5, sticky=NS+W)

    innhold_karakterer = StringVar()
    lst_karakterer = Listbox(vitnemål, width=60, listvariable=innhold_karakterer, yscrollcommand=y_scroll.set)
    lst_karakterer.grid(row=2, column=0, columnspan=5, rowspan=5, padx=(25,0), pady=5, sticky=E)
    y_scroll['command']=lst_karakterer.yview

    #Knapp for å lukke vinduet
    btn_lukk_vindu = Button(vitnemål, text='Lukk vindu', command=vitnemål.destroy)
    btn_lukk_vindu.grid(row=7, column=5, padx=5, pady=5, sticky=W)

    vitnemål.mainloop()
    
#Hovedmeny
hovedmeny = Tk()
hovedmeny.title('Oblig2 - Hovedmeny')

#Labels til hovedmenyen
lbl_ajour = Label(hovedmeny, text='Liste over fremtidige eksamener:')
lbl_ajour.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky=E)

lbl_etter_dato = Label(hovedmeny, text='Finn eksamener etter dato:')
lbl_etter_dato.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky=E)

lbl_karakterliste = Label(hovedmeny, text='Skriv ut karakterliste:')
lbl_karakterliste.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky=E)

lbl_registrer_karakter = Label(hovedmeny, text='Registrere karakterer for en avholdt eksamen:')
lbl_registrer_karakter.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky=E)

lbl_karakterfordeling = Label(hovedmeny, text='Skriv ut karakterstatistikk:')
lbl_karakterfordeling.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky=E)

lbl_eksamensresultater = Label(hovedmeny, text='Skriv ut eksamensresultater for en student:')
lbl_eksamensresultater.grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky=E)

lbl_vitnemål = Label(hovedmeny, text='Skriv ut vitnemål for en student:')
lbl_vitnemål.grid(row=7, column=0, columnspan=3, padx=5, pady=5, sticky=E)

#Buttons til hovedmenyen
btn_ajour = Button(hovedmeny, text='Eksamener', command=ajourholding)
btn_ajour.grid(row=1, column=4, columnspan=2, padx=5, pady=5, sticky=W)

btn_etter_dato = Button(hovedmeny, text='Dato', command=etter_dato)
btn_etter_dato.grid(row=2, column=4, columnspan=2, padx=5, pady=5, sticky=W)

btn_karakterliste = Button(hovedmeny, text='Karakterliste', command=karakterlisteGUI)
btn_karakterliste.grid(row=3, column=4, columnspan=2, padx=5, pady=5, sticky=W)

btn_registrer_karakter = Button(hovedmeny, text='Registrer Karakterer', command=registrer_karakterGUI)
btn_registrer_karakter.grid(row=4, column=4, columnspan=2, padx=5, pady=5, sticky=W)

btn_karakterfordeling = Button(hovedmeny, text='Karakterfordeling', command=karakterfordelingGUI)
btn_karakterfordeling.grid(row=5, column=4, columnspan=2, padx=5, pady=5, sticky=W)

btn_eksamensresultater = Button(hovedmeny, text='Eksamensresultater', command=eksamensresultaterGUI)
btn_eksamensresultater.grid(row=6, column=4, columnspan=2, padx=5, pady=5, sticky=W)

btn_vitnemål = Button(hovedmeny, text='Vitnemål', command=vitnemålGUI)
btn_vitnemål.grid(row=7, column=4, columnspan=2, padx=5, pady=5, sticky=W)

#Knapp for å avslutte programmet
btn_avslutt = Button(hovedmeny, text='Avslutt', command=lambda:[hovedmeny.destroy(), database.close()])
btn_avslutt.grid(row=8, column=6, padx=5, pady=5, sticky=W)

hovedmeny.mainloop()
