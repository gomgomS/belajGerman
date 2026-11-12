// Seed dump JSON per tipe tes (Hören, Lesen, Schreiben) ke db_test_type_dump.
// Jenis: single, grouped (pilihan ganda), rf_single, rf_grouped (Richtig/Falsch), cloze (Lückentext).
// Jalankan: mongosh german_platform seed_test_type_dumps.js
// Aman dijalankan ulang: dump dengan judul yang sama untuk tipe & jenis yang sama dilewati.

const DUMPS = {

    // ════════════════════════════════════════════════════════════════════
    // HÖREN — tanpa audio dulu; transkrip ditulis di teks soal / bacaan
    // ════════════════════════════════════════════════════════════════════
    HOEREN: {
        single: [
            {
                question_text: '<p><em>Sie hören eine Durchsage am Bahnhof.</em></p><p>„Achtung an Gleis 5: Der ICE 578 nach Hamburg, planmäßige Abfahrt 14:32 Uhr, fährt heute mit circa 20 Minuten Verspätung ab.“</p><p><strong>Wann fährt der Zug voraussichtlich ab?</strong></p>',
                option_a: 'Um 14:12 Uhr',
                option_b: 'Um 14:32 Uhr',
                option_c: 'Um 14:52 Uhr',
                option_d: 'Um 15:32 Uhr',
                correct_answer: 'C',
                explanation: '<p><strong>Jawaban: C — Um 14:52 Uhr.</strong></p><p>Jadwal awal 14:32 dan kereta terlambat <em>circa 20 Minuten</em>, jadi berangkat sekitar 14:52.</p>'
            },
            {
                question_text: '<p><em>Sie hören eine Nachricht auf dem Anrufbeantworter.</em></p><p>„Hallo Frau Weber, hier ist die Praxis Dr. Klein. Ihr Termin am Donnerstag muss leider ausfallen. Können Sie stattdessen am Freitag um 10 Uhr kommen? Bitte rufen Sie uns kurz zurück.“</p><p><strong>Was soll Frau Weber tun?</strong></p>',
                option_a: 'Am Donnerstag in die Praxis kommen',
                option_b: 'Die Praxis zurückrufen',
                option_c: 'Einen neuen Arzt suchen',
                option_d: 'Am Freitag um 12 Uhr kommen',
                correct_answer: 'B',
                explanation: '<p><strong>Jawaban: B — Die Praxis zurückrufen.</strong></p><p>Kalimat terakhir: <em>Bitte rufen Sie uns kurz zurück.</em> Janji hari Kamis batal, dan tawaran pengganti jam 10, bukan jam 12.</p>'
            },
            {
                question_text: '<p><em>Sie hören den Wetterbericht im Radio.</em></p><p>„Und nun das Wetter für morgen: Am Vormittag ist es in ganz Bayern sonnig. Am Nachmittag ziehen von Westen Wolken auf und es kann regnen. Die Temperaturen liegen zwischen 18 und 22 Grad.“</p><p><strong>Wie wird das Wetter morgen Nachmittag?</strong></p>',
                option_a: 'Sonnig und sehr warm',
                option_b: 'Es schneit.',
                option_c: 'Es wird wolkig und vielleicht regnet es.',
                option_d: 'Es wird sehr kalt.',
                correct_answer: 'C',
                explanation: '<p><strong>Jawaban: C.</strong></p><p><em>Am Nachmittag ziehen Wolken auf und es kann regnen</em> — siang hari berawan dan mungkin hujan. Cerah hanya pada pagi hari.</p>'
            }
        ],
        grouped: [
            {
                title: 'Telefongespräch — Wohnungssuche',
                content_text: '<p><em>Sie hören ein Telefongespräch. Lesen Sie zuerst die Aufgaben 1–4.</em></p><p><strong>Transkript</strong></p><p><strong>Makler:</strong> Guten Tag, Hausverwaltung Schröder, was kann ich für Sie tun?</p><p><strong>Lisa:</strong> Guten Tag, mein Name ist Lisa Brandt. Ich rufe wegen der Wohnung in der Goethestraße an. Ist sie noch frei?</p><p><strong>Makler:</strong> Ja, die ist noch frei. Es ist eine Dreizimmerwohnung im zweiten Stock, 72 Quadratmeter, mit Balkon.</p><p><strong>Lisa:</strong> Und wie hoch ist die Miete?</p><p><strong>Makler:</strong> Die Kaltmiete beträgt 780 Euro, dazu kommen 170 Euro Nebenkosten, also insgesamt 950 Euro warm.</p><p><strong>Lisa:</strong> Darf man dort Haustiere halten? Ich habe eine Katze.</p><p><strong>Makler:</strong> Katzen sind kein Problem, aber Hunde sind leider nicht erlaubt. Und in der Wohnung darf nicht geraucht werden.</p><p><strong>Lisa:</strong> Kann ich die Wohnung bald besichtigen?</p><p><strong>Makler:</strong> Gern. Am Mittwoch um 17 Uhr habe ich noch einen Termin frei.</p><p><strong>Lisa:</strong> Mittwoch passt mir gut. Vielen Dank!</p>',
                questions: [
                    {
                        question_text: '<p>Wie viele Zimmer hat die Wohnung?</p>',
                        option_a: 'Zwei',
                        option_b: 'Drei',
                        option_c: 'Vier',
                        option_d: 'Zweiundsiebzig',
                        correct_answer: 'B',
                        explanation: '<p><strong>Jawaban: B — Drei.</strong></p><p><em>Eine Dreizimmerwohnung</em> = apartemen tiga kamar. Angka 72 adalah luas (m²).</p>'
                    },
                    {
                        question_text: '<p>Wie viel kostet die Wohnung insgesamt pro Monat?</p>',
                        option_a: '170 Euro',
                        option_b: '780 Euro',
                        option_c: '950 Euro',
                        option_d: '720 Euro',
                        correct_answer: 'C',
                        explanation: '<p><strong>Jawaban: C — 950 Euro.</strong></p><p>Kaltmiete 780 € + Nebenkosten 170 € = <em>950 Euro warm</em>.</p>'
                    },
                    {
                        question_text: '<p>Was ist in der Wohnung nicht erlaubt?</p>',
                        option_a: 'Eine Katze halten',
                        option_b: 'Den Balkon benutzen',
                        option_c: 'In der Wohnung rauchen',
                        option_d: 'Besuch bekommen',
                        correct_answer: 'C',
                        explanation: '<p><strong>Jawaban: C — In der Wohnung rauchen.</strong></p><p><em>In der Wohnung darf nicht geraucht werden.</em> Kucing justru boleh (<em>Katzen sind kein Problem</em>).</p>'
                    },
                    {
                        question_text: '<p>Wann kann Lisa die Wohnung besichtigen?</p>',
                        option_a: 'Am Montag um 17 Uhr',
                        option_b: 'Am Mittwoch um 17 Uhr',
                        option_c: 'Am Mittwoch um 7 Uhr',
                        option_d: 'Am Freitag um 17 Uhr',
                        correct_answer: 'B',
                        explanation: '<p><strong>Jawaban: B — Am Mittwoch um 17 Uhr.</strong></p><p>Makler: <em>Am Mittwoch um 17 Uhr habe ich noch einen Termin frei.</em> Lisa setuju.</p>'
                    }
                ]
            },
            {
                title: 'Radiointerview — Ehrenamt bei der Tafel',
                content_text: '<p><em>Sie hören ein Interview im Radio. Lesen Sie zuerst die Aufgaben 1–4.</em></p><p><strong>Transkript</strong></p><p><strong>Moderatorin:</strong> Heute ist Jonas Meier bei uns im Studio. Jonas, Sie arbeiten ehrenamtlich bei der Tafel. Was machen Sie dort genau?</p><p><strong>Jonas:</strong> Wir sammeln Lebensmittel, die Supermärkte nicht mehr verkaufen können, und geben sie an Menschen mit wenig Geld weiter. Ich fahre meistens den Lieferwagen und hole die Lebensmittel ab.</p><p><strong>Moderatorin:</strong> Wie viel Zeit investieren Sie?</p><p><strong>Jonas:</strong> Ungefähr sechs Stunden pro Woche, immer dienstags und samstags. Unter der Woche studiere ich ja noch Informatik.</p><p><strong>Moderatorin:</strong> Warum haben Sie damit angefangen?</p><p><strong>Jonas:</strong> Ehrlich gesagt hat mich meine Großmutter darauf gebracht. Sie hat dort zwanzig Jahre lang geholfen. Als sie aufhören musste, wollte ich weitermachen.</p><p><strong>Moderatorin:</strong> Was gefällt Ihnen am meisten?</p><p><strong>Jonas:</strong> Der Kontakt mit den Menschen. Viele Kunden kenne ich inzwischen mit Namen, und wir trinken oft zusammen einen Kaffee.</p>',
                questions: [
                    {
                        question_text: '<p>Was macht Jonas bei der Tafel hauptsächlich?</p>',
                        option_a: 'Er kocht Essen für die Kunden.',
                        option_b: 'Er fährt den Lieferwagen und holt Lebensmittel ab.',
                        option_c: 'Er verkauft Lebensmittel im Supermarkt.',
                        option_d: 'Er organisiert Spenden im Internet.',
                        correct_answer: 'B',
                        explanation: '<p><strong>Jawaban: B.</strong></p><p><em>Ich fahre meistens den Lieferwagen und hole die Lebensmittel ab.</em></p>'
                    },
                    {
                        question_text: '<p>Wie oft arbeitet Jonas bei der Tafel?</p>',
                        option_a: 'Jeden Tag',
                        option_b: 'Zweimal pro Woche',
                        option_c: 'Einmal im Monat',
                        option_d: 'Nur sonntags',
                        correct_answer: 'B',
                        explanation: '<p><strong>Jawaban: B — Zweimal pro Woche.</strong></p><p><em>Immer dienstags und samstags</em> = Selasa dan Sabtu, jadi dua kali seminggu.</p>'
                    },
                    {
                        question_text: '<p>Warum hat Jonas mit dem Ehrenamt angefangen?</p>',
                        option_a: 'Er brauchte es für sein Studium.',
                        option_b: 'Ein Freund hat ihn gefragt.',
                        option_c: 'Seine Großmutter hat dort geholfen.',
                        option_d: 'Er wollte Geld verdienen.',
                        correct_answer: 'C',
                        explanation: '<p><strong>Jawaban: C.</strong></p><p><em>Meine Großmutter hat mich darauf gebracht … Als sie aufhören musste, wollte ich weitermachen.</em></p>'
                    },
                    {
                        question_text: '<p>Was gefällt Jonas am meisten?</p>',
                        option_a: 'Das Autofahren',
                        option_b: 'Der Kontakt mit den Menschen',
                        option_c: 'Der kostenlose Kaffee',
                        option_d: 'Die kurzen Arbeitszeiten',
                        correct_answer: 'B',
                        explanation: '<p><strong>Jawaban: B — Der Kontakt mit den Menschen.</strong></p><p>Jonas menjawab langsung: <em>Der Kontakt mit den Menschen.</em> Kopi hanya contoh kebersamaan, bukan alasan utama.</p>'
                    }
                ]
            },
            {
                title: 'Durchsagen — Flughafen, Supermarkt, Museum, U-Bahn',
                content_text: '<p><em>Sie hören vier kurze Durchsagen. Zu jeder Durchsage gibt es eine Aufgabe.</em></p><p><strong>Durchsage 1 (Flughafen):</strong> „Letzter Aufruf für Passagiere des Fluges LH 2024 nach Wien. Bitte begeben Sie sich sofort zum Ausgang B 14. Der Ausgang wird in fünf Minuten geschlossen.“</p><p><strong>Durchsage 2 (Supermarkt):</strong> „Liebe Kundinnen und Kunden, heute bis 20 Uhr gibt es in unserer Obstabteilung alle Äpfel und Birnen zum halben Preis.“</p><p><strong>Durchsage 3 (Museum):</strong> „Sehr geehrte Besucher, das Museum schließt in 30 Minuten. Die Cafeteria im Erdgeschoss ist bereits geschlossen. Wir bitten Sie, sich langsam zum Ausgang zu begeben.“</p><p><strong>Durchsage 4 (U-Bahn):</strong> „Wegen Bauarbeiten fährt die U3 zwischen Marienplatz und Odeonsplatz am Wochenende nicht. Bitte benutzen Sie die Ersatzbusse.“</p>',
                questions: [
                    {
                        question_text: '<p><strong>Durchsage 1:</strong> Wohin sollen die Passagiere gehen?</p>',
                        option_a: 'Zum Check-in',
                        option_b: 'Zum Ausgang B 14',
                        option_c: 'Zur Gepäckausgabe',
                        option_d: 'Zum Ausgang B 40',
                        correct_answer: 'B',
                        explanation: '<p><strong>Jawaban: B — Zum Ausgang B 14.</strong></p><p><em>Bitte begeben Sie sich sofort zum Ausgang B 14.</em> Hati-hati angka 14 vs 40.</p>'
                    },
                    {
                        question_text: '<p><strong>Durchsage 2:</strong> Was ist heute billiger?</p>',
                        option_a: 'Brot',
                        option_b: 'Äpfel und Birnen',
                        option_c: 'Gemüse',
                        option_d: 'Getränke',
                        correct_answer: 'B',
                        explanation: '<p><strong>Jawaban: B — Äpfel und Birnen.</strong></p><p><em>Zum halben Preis</em> = setengah harga, untuk apel dan pir di bagian buah.</p>'
                    },
                    {
                        question_text: '<p><strong>Durchsage 3:</strong> Was ist schon geschlossen?</p>',
                        option_a: 'Das Museum',
                        option_b: 'Der Ausgang',
                        option_c: 'Die Cafeteria',
                        option_d: 'Der Museumsshop',
                        correct_answer: 'C',
                        explanation: '<p><strong>Jawaban: C — Die Cafeteria.</strong></p><p><em>Die Cafeteria ist bereits geschlossen.</em> Museumnya baru tutup 30 menit lagi.</p>'
                    },
                    {
                        question_text: '<p><strong>Durchsage 4:</strong> Was sollen die Fahrgäste am Wochenende tun?</p>',
                        option_a: 'Ein Taxi nehmen',
                        option_b: 'Zu Fuß gehen',
                        option_c: 'Die Ersatzbusse benutzen',
                        option_d: 'Die U6 nehmen',
                        correct_answer: 'C',
                        explanation: '<p><strong>Jawaban: C — Die Ersatzbusse benutzen.</strong></p><p><em>Bitte benutzen Sie die Ersatzbusse</em> = gunakan bus pengganti.</p>'
                    }
                ]
            }
        ]
    },

    // ════════════════════════════════════════════════════════════════════
    // LESEN
    // ════════════════════════════════════════════════════════════════════
    LESEN: {
        single: [
            {
                question_text: '<p><em>Lesen Sie die Anzeige.</em></p><p>„Suche Nachhilfe in Mathematik für meinen Sohn (8. Klasse), zweimal pro Woche nachmittags. Bezahlung nach Vereinbarung. Tel. 0176 2345678“</p><p><strong>Was sucht die Person?</strong></p>',
                option_a: 'Einen Mathelehrer für sich selbst',
                option_b: 'Nachhilfe für ihr Kind',
                option_c: 'Eine Stelle als Lehrerin',
                option_d: 'Einen Platz an einer Schule',
                correct_answer: 'B',
                explanation: '<p><strong>Jawaban: B — Nachhilfe für ihr Kind.</strong></p><p><em>Nachhilfe … für meinen Sohn</em> = les tambahan untuk anaknya, bukan untuk dirinya sendiri.</p>'
            },
            {
                question_text: '<p><em>Lesen Sie den Aushang im Schwimmbad.</em></p><p>„Liebe Gäste, das Schwimmbad bleibt wegen Reinigungsarbeiten vom 3. bis 7. Juni geschlossen. Die Sauna ist in dieser Zeit normal geöffnet.“</p><p><strong>Was ist richtig?</strong></p>',
                option_a: 'Die Sauna ist auch geschlossen.',
                option_b: 'Man kann am 5. Juni in die Sauna gehen.',
                option_c: 'Das Schwimmbad ist ab dem 3. Juni wieder offen.',
                option_d: 'Das Schwimmbad schließt für immer.',
                correct_answer: 'B',
                explanation: '<p><strong>Jawaban: B.</strong></p><p>Kolam tutup 3–7 Juni, tetapi <em>die Sauna ist in dieser Zeit normal geöffnet</em>, jadi tanggal 5 Juni sauna tetap buka.</p>'
            },
            {
                question_text: '<p><em>Lesen Sie den Satz aus einer E-Mail und ergänzen Sie.</em></p><p>„Ich freue mich schon sehr ______ unser Treffen nächste Woche.“</p>',
                option_a: 'über',
                option_b: 'auf',
                option_c: 'an',
                option_d: 'für',
                correct_answer: 'B',
                explanation: '<p><strong>Jawaban: B — auf.</strong></p><p><em>sich freuen auf + Akk.</em> untuk hal yang akan datang (<em>nächste Woche</em>). <em>sich freuen über</em> dipakai untuk hal yang sudah/sedang terjadi.</p>'
            }
        ],
        grouped: [
            {
                title: 'Zeitungsartikel — Arbeiten von zu Hause',
                content_text: '<p><em>Lesen Sie den Text und lösen Sie die Aufgaben 1–4.</em></p><p><strong>Arbeiten von zu Hause – Fluch oder Segen?</strong></p><p>Seit einigen Jahren arbeiten in Deutschland immer mehr Menschen von zu Hause aus. Laut einer aktuellen Umfrage verbringt fast jeder vierte Beschäftigte mindestens einen Tag pro Woche im Homeoffice. Besonders in Büroberufen ist diese Arbeitsform heute ganz normal.</p><p>Viele Arbeitnehmer schätzen die Vorteile: Sie sparen den Weg zur Arbeit, können ihre Zeit flexibler einteilen und Familie und Beruf besser verbinden. Auch die Umwelt profitiert, weil weniger Menschen mit dem Auto ins Büro fahren.</p><p>Doch es gibt auch Nachteile. Manche Beschäftigte fühlen sich zu Hause einsam, weil der Kontakt zu den Kollegen fehlt. Andere haben Schwierigkeiten, nach Feierabend wirklich abzuschalten, weil der Laptop immer in der Nähe ist. Experten empfehlen deshalb feste Arbeitszeiten und einen eigenen Arbeitsplatz in der Wohnung.</p>',
                questions: [
                    {
                        question_text: '<p>Worum geht es im Text hauptsächlich?</p>',
                        option_a: 'Wie man einen Job im Büro findet',
                        option_b: 'Um Vor- und Nachteile der Arbeit von zu Hause',
                        option_c: 'Warum das Homeoffice verboten werden soll',
                        option_d: 'Um die Geschichte der Büroarbeit',
                        correct_answer: 'B',
                        explanation: '<p><strong>Jawaban: B.</strong></p><p>Paragraf 2 membahas <em>Vorteile</em>, paragraf 3 membahas <em>Nachteile</em> bekerja dari rumah.</p>'
                    },
                    {
                        question_text: '<p>Wie viele Beschäftigte arbeiten mindestens einen Tag pro Woche zu Hause?</p>',
                        option_a: 'Fast alle',
                        option_b: 'Etwa die Hälfte',
                        option_c: 'Fast jeder vierte',
                        option_d: 'Nur Menschen in Büroberufen',
                        correct_answer: 'C',
                        explanation: '<p><strong>Jawaban: C — Fast jeder vierte.</strong></p><p><em>Fast jeder vierte Beschäftigte</em> = hampir satu dari empat pekerja (±25%).</p>'
                    },
                    {
                        question_text: '<p>Welcher Vorteil wird im Text genannt?</p>',
                        option_a: 'Man verdient mehr Geld.',
                        option_b: 'Man spart den Weg zur Arbeit.',
                        option_c: 'Man hat mehr Kontakt zu Kollegen.',
                        option_d: 'Man braucht keinen Laptop.',
                        correct_answer: 'B',
                        explanation: '<p><strong>Jawaban: B.</strong></p><p><em>Sie sparen den Weg zur Arbeit.</em> Kontak dengan kolega justru disebut sebagai kekurangan.</p>'
                    },
                    {
                        question_text: '<p>Was empfehlen Experten?</p>',
                        option_a: 'Nur noch im Büro zu arbeiten',
                        option_b: 'Den Laptop abends öfter zu benutzen',
                        option_c: 'Feste Arbeitszeiten und einen eigenen Arbeitsplatz',
                        option_d: 'Öfter mit dem Auto zu fahren',
                        correct_answer: 'C',
                        explanation: '<p><strong>Jawaban: C.</strong></p><p><em>Experten empfehlen deshalb feste Arbeitszeiten und einen eigenen Arbeitsplatz in der Wohnung.</em></p>'
                    }
                ]
            },
            {
                title: 'E-Mail — Annas Umzug nach Leipzig',
                content_text: '<p><em>Lesen Sie die E-Mail und lösen Sie die Aufgaben 1–4.</em></p><p>Liebe Sara,</p><p>vielen Dank für deine Nachricht! Entschuldige, dass ich erst jetzt antworte, aber die letzten Wochen waren total stressig. Wie du weißt, bin ich im März nach Leipzig gezogen, weil ich hier eine Stelle als Krankenpflegerin bekommen habe.</p><p>Die Arbeit im Krankenhaus gefällt mir sehr gut, auch wenn ich oft Nachtdienst habe. Meine Kolleginnen sind supernett und haben mir in der ersten Zeit viel geholfen.</p><p>Eine Wohnung zu finden war allerdings nicht leicht. Die ersten zwei Monate habe ich bei meiner Tante gewohnt. Jetzt habe ich endlich eine kleine Zweizimmerwohnung in der Nähe vom Hauptbahnhof gefunden.</p><p>Hast du Lust, mich im Sommer zu besuchen? Im Juli habe ich zwei Wochen Urlaub. Dann können wir zusammen die Stadt anschauen und an einen der Seen fahren.</p><p>Liebe Grüße<br>Anna</p>',
                questions: [
                    {
                        question_text: '<p>Warum ist Anna nach Leipzig gezogen?</p>',
                        option_a: 'Sie studiert dort.',
                        option_b: 'Ihre Tante wohnt dort.',
                        option_c: 'Sie hat dort eine Arbeit gefunden.',
                        option_d: 'Sie wollte an einem See wohnen.',
                        correct_answer: 'C',
                        explanation: '<p><strong>Jawaban: C.</strong></p><p><em>… weil ich hier eine Stelle als Krankenpflegerin bekommen habe.</em></p>'
                    },
                    {
                        question_text: '<p>Was schreibt Anna über ihre Arbeit?</p>',
                        option_a: 'Sie arbeitet nie nachts.',
                        option_b: 'Sie mag die Arbeit und die Kolleginnen.',
                        option_c: 'Die Kolleginnen helfen ihr nicht.',
                        option_d: 'Sie sucht eine neue Stelle.',
                        correct_answer: 'B',
                        explanation: '<p><strong>Jawaban: B.</strong></p><p><em>Die Arbeit gefällt mir sehr gut … Meine Kolleginnen sind supernett.</em> Ia justru sering <em>Nachtdienst</em>.</p>'
                    },
                    {
                        question_text: '<p>Wo hat Anna am Anfang gewohnt?</p>',
                        option_a: 'In einem Hotel',
                        option_b: 'Bei ihrer Tante',
                        option_c: 'In einer Zweizimmerwohnung',
                        option_d: 'Im Krankenhaus',
                        correct_answer: 'B',
                        explanation: '<p><strong>Jawaban: B — Bei ihrer Tante.</strong></p><p><em>Die ersten zwei Monate habe ich bei meiner Tante gewohnt.</em> Apartemen dua kamar baru ditemukan sekarang.</p>'
                    },
                    {
                        question_text: '<p>Was schlägt Anna vor?</p>',
                        option_a: 'Sara soll sie im Juli besuchen.',
                        option_b: 'Sie wollen im März zusammen Urlaub machen.',
                        option_c: 'Sara soll auch nach Leipzig ziehen.',
                        option_d: 'Sie treffen sich in Saras Stadt.',
                        correct_answer: 'A',
                        explanation: '<p><strong>Jawaban: A.</strong></p><p><em>Hast du Lust, mich im Sommer zu besuchen? Im Juli habe ich zwei Wochen Urlaub.</em></p>'
                    }
                ]
            },
            {
                title: 'Anzeigen zuordnen — Kurse, Fahrrad, Zimmer',
                content_text: '<p><em>Lesen Sie die Anzeigen A–D. Welche Anzeige passt zu welcher Person?</em></p><p><strong>Anzeige A</strong> — Sprachschule Lingua: Abendkurse Deutsch B1/B2, Montag und Mittwoch 18:30–20:00 Uhr, kleine Gruppen, Vorbereitung auf das Goethe-Zertifikat.</p><p><strong>Anzeige B</strong> — Fahrradwerkstatt Kette &amp; Co.: Reparaturen aller Art, auch samstags 9–14 Uhr geöffnet. Gebrauchte Fahrräder schon ab 80 Euro.</p><p><strong>Anzeige C</strong> — Kochkurs „Italienisch für Anfänger“: jeden Freitag 17–20 Uhr, gemeinsames Abendessen inklusive, 35 Euro pro Abend.</p><p><strong>Anzeige D</strong> — WG sucht Mitbewohnerin: helles Zimmer, 18 m², 390 Euro warm, fünf Minuten zur Universität, frei ab 1. Oktober.</p>',
                questions: [
                    {
                        question_text: '<p>Mehmet arbeitet tagsüber und möchte abends sein Deutsch verbessern, weil er bald eine Prüfung machen will.</p>',
                        option_a: 'Anzeige A',
                        option_b: 'Anzeige B',
                        option_c: 'Anzeige C',
                        option_d: 'Anzeige D',
                        correct_answer: 'A',
                        explanation: '<p><strong>Jawaban: A.</strong></p><p>Kursus malam (<em>Abendkurse</em>) dengan persiapan ujian Goethe-Zertifikat.</p>'
                    },
                    {
                        question_text: '<p>Julia beginnt im Oktober ihr Studium und sucht ein günstiges Zimmer in der Nähe der Uni.</p>',
                        option_a: 'Anzeige A',
                        option_b: 'Anzeige B',
                        option_c: 'Anzeige C',
                        option_d: 'Anzeige D',
                        correct_answer: 'D',
                        explanation: '<p><strong>Jawaban: D.</strong></p><p>Kamar WG, <em>fünf Minuten zur Universität</em>, tersedia <em>ab 1. Oktober</em>.</p>'
                    },
                    {
                        question_text: '<p>Tom braucht ein billiges Fahrrad und hat nur am Wochenende Zeit.</p>',
                        option_a: 'Anzeige A',
                        option_b: 'Anzeige B',
                        option_c: 'Anzeige C',
                        option_d: 'Anzeige D',
                        correct_answer: 'B',
                        explanation: '<p><strong>Jawaban: B.</strong></p><p>Sepeda bekas mulai 80 € dan bengkel juga buka hari Sabtu (<em>auch samstags</em>).</p>'
                    },
                    {
                        question_text: '<p>Lena möchte neue Rezepte lernen und am Freitagabend mit anderen Leuten zusammen essen.</p>',
                        option_a: 'Anzeige A',
                        option_b: 'Anzeige B',
                        option_c: 'Anzeige C',
                        option_d: 'Anzeige D',
                        correct_answer: 'C',
                        explanation: '<p><strong>Jawaban: C.</strong></p><p>Kursus masak setiap Jumat dengan makan malam bersama (<em>gemeinsames Abendessen inklusive</em>).</p>'
                    }
                ]
            }
        ]
    },

    // ════════════════════════════════════════════════════════════════════
    // SCHREIBEN — pilihan ganda tentang cara menulis (salam, register, konektor)
    // ════════════════════════════════════════════════════════════════════
    SCHREIBEN: {
        single: [
            {
                question_text: '<p>Sie schreiben eine E-Mail an eine Firma, kennen aber den Namen der Person nicht. <strong>Wie beginnen Sie die E-Mail?</strong></p>',
                option_a: 'Hallo Leute,',
                option_b: 'Sehr geehrte Damen und Herren,',
                option_c: 'Liebe Frau,',
                option_d: 'Hi!',
                correct_answer: 'B',
                explanation: '<p><strong>Jawaban: B.</strong></p><p><em>Sehr geehrte Damen und Herren</em> adalah salam formal standar bila nama penerima tidak diketahui.</p>'
            },
            {
                question_text: '<p><strong>Welcher Gruß passt am Ende eines formellen Briefes?</strong></p>',
                option_a: 'Bis bald!',
                option_b: 'Tschüss',
                option_c: 'Mit freundlichen Grüßen',
                option_d: 'Liebe Grüße und Küsse',
                correct_answer: 'C',
                explanation: '<p><strong>Jawaban: C — Mit freundlichen Grüßen.</strong></p><p>Penutup formal standar. Pilihan lain bersifat informal.</p>'
            },
            {
                question_text: '<p>Ergänzen Sie den Satz.</p><p>„Ich kann leider nicht zu deiner Party kommen, ______ ich an diesem Tag arbeiten muss.“</p>',
                option_a: 'deshalb',
                option_b: 'weil',
                option_c: 'trotzdem',
                option_d: 'aber',
                correct_answer: 'B',
                explanation: '<p><strong>Jawaban: B — weil.</strong></p><p>Anak kalimat alasan dengan verba di akhir: <em>…, weil ich an diesem Tag arbeiten <strong>muss</strong>.</em> <em>deshalb/trotzdem</em> menuntut verba di posisi 2.</p>'
            }
        ],
        grouped: [
            {
                title: 'Informelle E-Mail — Absage an Paul',
                content_text: '<p><em>Situation:</em> Ihr Freund Paul hat Sie zu seiner Geburtstagsparty am Samstag eingeladen. Sie können nicht kommen.</p><p><strong>Schreiben Sie eine E-Mail an Paul:</strong></p><ul><li>Bedanken Sie sich für die Einladung.</li><li>Sagen Sie ab und nennen Sie einen Grund.</li><li>Machen Sie einen Vorschlag für ein anderes Treffen.</li></ul><p><em>Beantworten Sie die Aufgaben 1–4: Welche Formulierung passt am besten?</em></p>',
                questions: [
                    {
                        question_text: '<p>Welche Anrede passt?</p>',
                        option_a: 'Sehr geehrter Herr Paul,',
                        option_b: 'Lieber Paul,',
                        option_c: 'Hallo Herr Schneider,',
                        option_d: 'Sehr geehrte Damen und Herren,',
                        correct_answer: 'B',
                        explanation: '<p><strong>Jawaban: B — Lieber Paul,</strong></p><p>E-mail kepada teman memakai salam informal <em>Lieber/Liebe + nama depan</em>.</p>'
                    },
                    {
                        question_text: '<p>Welcher Satz ist eine höfliche Absage mit Grund?</p>',
                        option_a: 'Ich komme nicht.',
                        option_b: 'Leider kann ich nicht kommen, weil ich an diesem Wochenende bei meinen Eltern bin.',
                        option_c: 'Deine Party ist mir egal.',
                        option_d: 'Vielleicht komme ich, vielleicht auch nicht.',
                        correct_answer: 'B',
                        explanation: '<p><strong>Jawaban: B.</strong></p><p>Ada kata <em>Leider</em> (sopan) dan alasan dengan <em>weil</em>, sesuai poin tugas.</p>'
                    },
                    {
                        question_text: '<p>Welcher Satz ist ein guter Vorschlag für ein anderes Treffen?</p>',
                        option_a: 'Wollen wir uns nächste Woche zum Essen treffen?',
                        option_b: 'Du musst mich besuchen.',
                        option_c: 'Ich habe keine Zeit für dich.',
                        option_d: 'Ein Treffen ist schwierig.',
                        correct_answer: 'A',
                        explanation: '<p><strong>Jawaban: A.</strong></p><p>Usulan yang ramah memakai pertanyaan <em>Wollen wir …?</em> / <em>Hast du Lust …?</em></p>'
                    },
                    {
                        question_text: '<p>Welcher Schluss passt zu dieser E-Mail?</p>',
                        option_a: 'Mit freundlichen Grüßen, Ihr Max',
                        option_b: 'Hochachtungsvoll',
                        option_c: 'Viele Grüße, dein Max',
                        option_d: 'Sehr geehrter Max',
                        correct_answer: 'C',
                        explanation: '<p><strong>Jawaban: C.</strong></p><p>Penutup informal <em>Viele Grüße, dein …</em> cocok untuk teman; A dan B terlalu formal.</p>'
                    }
                ]
            },
            {
                title: 'Formelle E-Mail — Beschwerde an ein Hotel',
                content_text: '<p><em>Situation:</em> Sie haben vom 12. bis 14. Mai im Hotel Seeblick übernachtet. Das Zimmer war sehr laut und das WLAN hat nicht funktioniert.</p><p><strong>Schreiben Sie eine Beschwerde an das Hotel:</strong></p><ul><li>Nennen Sie den Grund Ihres Schreibens.</li><li>Beschreiben Sie die Probleme.</li><li>Sagen Sie, was Sie erwarten.</li></ul><p><em>Beantworten Sie die Aufgaben 1–4: Welche Formulierung passt am besten?</em></p>',
                questions: [
                    {
                        question_text: '<p>Welcher Satz ist eine passende Einleitung?</p>',
                        option_a: 'Hey, euer Hotel war echt schlecht.',
                        option_b: 'Ich wende mich an Sie, weil ich mit meinem Aufenthalt vom 12. bis 14. Mai leider nicht zufrieden war.',
                        option_c: 'Ich schreibe, weil mir langweilig ist.',
                        option_d: 'Wie geht es dir?',
                        correct_answer: 'B',
                        explanation: '<p><strong>Jawaban: B.</strong></p><p>Pembuka formal yang langsung menyebut alasan menulis (<em>Ich wende mich an Sie, weil …</em>).</p>'
                    },
                    {
                        question_text: '<p>Welche Formulierung beschreibt das Problem sachlich?</p>',
                        option_a: 'Das WLAN war totaler Mist.',
                        option_b: 'Leider funktionierte das WLAN während meines gesamten Aufenthalts nicht.',
                        option_c: 'Euer WLAN ist das schlechteste der Welt!',
                        option_d: 'WLAN? Fehlanzeige!!!',
                        correct_answer: 'B',
                        explanation: '<p><strong>Jawaban: B.</strong></p><p>Keluhan formal harus objektif dan sopan, tanpa kata kasar atau tanda seru berlebihan.</p>'
                    },
                    {
                        question_text: '<p>Wie formulieren Sie Ihre Erwartung höflich?</p>',
                        option_a: 'Gebt mir sofort mein Geld zurück!',
                        option_b: 'Ich bitte Sie daher, mir einen Teil des Zimmerpreises zu erstatten.',
                        option_c: 'Ich will Geld.',
                        option_d: 'Vielleicht könnten Sie eventuell möglicherweise etwas tun.',
                        correct_answer: 'B',
                        explanation: '<p><strong>Jawaban: B.</strong></p><p>Permintaan jelas dan sopan: <em>Ich bitte Sie daher, …</em>. D terlalu kabur.</p>'
                    },
                    {
                        question_text: '<p>Welche Anredeform verwendet man in einer formellen Beschwerde?</p>',
                        option_a: 'du / dein',
                        option_b: 'Sie / Ihr',
                        option_c: 'ihr / euer',
                        option_d: 'man / sein',
                        correct_answer: 'B',
                        explanation: '<p><strong>Jawaban: B — Sie / Ihr.</strong></p><p>Surat formal selalu memakai bentuk sopan <em>Sie</em> (dan <em>Ihr</em> huruf besar).</p>'
                    }
                ]
            },
            {
                title: 'Forumsbeitrag — Smartphones für Kinder?',
                content_text: '<p><em>Situation:</em> In einem Online-Forum wird diskutiert: <strong>„Sollten Kinder unter zwölf Jahren ein eigenes Smartphone haben?“</strong></p><p><strong>Schreiben Sie Ihre Meinung (ca. 80 Wörter):</strong></p><ul><li>Sagen Sie Ihre Meinung.</li><li>Nennen Sie ein Argument und ein Gegenargument.</li><li>Schreiben Sie einen Schlusssatz.</li></ul><p><em>Beantworten Sie die Aufgaben 1–4: Welche Formulierung passt am besten?</em></p>',
                questions: [
                    {
                        question_text: '<p>Wie leiten Sie Ihre Meinung am besten ein?</p>',
                        option_a: 'Meiner Meinung nach sollten Kinder erst ab zwölf Jahren ein eigenes Smartphone bekommen.',
                        option_b: 'Smartphone.',
                        option_c: 'Kinder sind manchmal laut.',
                        option_d: 'Ich weiß nicht, was ein Smartphone ist.',
                        correct_answer: 'A',
                        explanation: '<p><strong>Jawaban: A.</strong></p><p><em>Meiner Meinung nach …</em> menyatakan pendapat dengan jelas dan sesuai topik.</p>'
                    },
                    {
                        question_text: '<p>Welcher Ausdruck leitet ein Gegenargument ein?</p>',
                        option_a: 'außerdem',
                        option_b: 'zum Beispiel',
                        option_c: 'auf der anderen Seite',
                        option_d: 'deshalb',
                        correct_answer: 'C',
                        explanation: '<p><strong>Jawaban: C — auf der anderen Seite.</strong></p><p><em>außerdem</em> = menambah argumen, <em>zum Beispiel</em> = contoh, <em>deshalb</em> = akibat.</p>'
                    },
                    {
                        question_text: '<p>Welcher Satz ist grammatisch richtig?</p>',
                        option_a: 'Ein Smartphone ist praktisch, weil die Eltern können ihre Kinder anrufen.',
                        option_b: 'Ein Smartphone ist praktisch, weil die Eltern ihre Kinder anrufen können.',
                        option_c: 'Ein Smartphone ist praktisch, weil können die Eltern ihre Kinder anrufen.',
                        option_d: 'Ein Smartphone ist praktisch, weil die Eltern können anrufen ihre Kinder.',
                        correct_answer: 'B',
                        explanation: '<p><strong>Jawaban: B.</strong></p><p>Setelah <em>weil</em>, verba terkonjugasi (<em>können</em>) berada di akhir kalimat.</p>'
                    },
                    {
                        question_text: '<p>Welcher Satz passt als Schluss?</p>',
                        option_a: 'Zusammenfassend finde ich, dass ein Smartphone für Kinder sinnvoll sein kann, wenn die Eltern klare Regeln festlegen.',
                        option_b: 'Tschüss!',
                        option_c: 'Das ist alles.',
                        option_d: 'Ich habe keine Meinung.',
                        correct_answer: 'A',
                        explanation: '<p><strong>Jawaban: A.</strong></p><p><em>Zusammenfassend …</em> merangkum pendapat; pilihan lain tidak menutup argumen.</p>'
                    }
                ]
            }
        ]
    }
};

// ════════════════════════════════════════════════════════════════════════════
// Richtig/Falsch (rf_*) & Lückentext (cloze)
// RF: tanpa option — correct_answer A = Richtig, B = Falsch.
// Cloze: content_text berisi [n]; tiap soal = satu rumpang (gap_no), tanpa gambar.
// ════════════════════════════════════════════════════════════════════════════
const EXTRA_DUMPS = {

    HOEREN: {
        rf_single: [
            {
                question_text: '<p><em>Sie hören eine Durchsage am Bahnhof.</em></p><p>„Liebe Fahrgäste, wegen eines technischen Defekts fällt der Regionalexpress nach Nürnberg um 16:10 Uhr heute aus. Bitte nehmen Sie den nächsten Zug um 16:40 Uhr von Gleis 3.“</p><p><strong>Der Zug um 16:10 Uhr fährt heute nicht.</strong></p>',
                correct_answer: 'A',
                explanation: '<p><strong>Richtig.</strong> <em>… fällt der Regionalexpress … um 16:10 Uhr heute aus</em> — <em>ausfallen</em> = dibatalkan, jadi kereta itu tidak berangkat.</p>'
            },
            {
                question_text: '<p><em>Sie hören eine Nachricht auf dem Anrufbeantworter.</em></p><p>„Hallo Tim, hier ist Sabine. Das Kino heute Abend klappt leider nicht, ich muss länger arbeiten. Wollen wir am Samstag gehen? Ruf mich an!“</p><p><strong>Sabine möchte heute Abend ins Kino gehen.</strong></p>',
                correct_answer: 'B',
                explanation: '<p><strong>Falsch.</strong> <em>Das Kino heute Abend klappt leider nicht</em> — Sabine membatalkan dan mengusulkan hari Sabtu.</p>'
            },
            {
                question_text: '<p><em>Sie hören eine Information im Radio.</em></p><p>„Am Wochenende findet auf dem Marktplatz das Stadtfest statt. Der Eintritt ist frei, nur für das Konzert am Samstagabend braucht man ein Ticket.“</p><p><strong>Für das ganze Stadtfest muss man Eintritt bezahlen.</strong></p>',
                correct_answer: 'B',
                explanation: '<p><strong>Falsch.</strong> <em>Der Eintritt ist frei</em> — hanya konser Sabtu malam yang perlu tiket.</p>'
            }
        ],
        rf_grouped: [
            {
                title: 'Gespräch im Reisebüro — Richtig oder Falsch?',
                content_text: '<p><em>Sie hören ein Gespräch. Sind die Aussagen 1–4 richtig oder falsch?</em></p><p><strong>Transkript</strong></p><p><strong>Kundin:</strong> Guten Tag, ich möchte im August mit meiner Tochter zwei Wochen nach Spanien fahren.</p><p><strong>Mitarbeiter:</strong> Gern. Möchten Sie fliegen oder mit dem Zug fahren?</p><p><strong>Kundin:</strong> Wir möchten fliegen, am liebsten ab Frankfurt. Das Hotel sollte direkt am Strand liegen.</p><p><strong>Mitarbeiter:</strong> Ich habe ein schönes Hotel auf Mallorca, 200 Meter vom Strand, mit Frühstück. Zwei Wochen kosten für Sie beide 1.400 Euro.</p><p><strong>Kundin:</strong> Das passt gut. Mehr als 1.500 Euro möchte ich nicht ausgeben. Ist das Frühstück wirklich dabei?</p><p><strong>Mitarbeiter:</strong> Ja, Frühstück ist inklusive. Das Abendessen kostet extra.</p>',
                questions: [
                    { question_text: '<p>Die Frau reist allein.</p>', correct_answer: 'B',
                      explanation: '<p><strong>Falsch.</strong> Ia pergi <em>mit meiner Tochter</em> (bersama putrinya).</p>' },
                    { question_text: '<p>Sie möchte mit dem Flugzeug reisen.</p>', correct_answer: 'A',
                      explanation: '<p><strong>Richtig.</strong> <em>Wir möchten fliegen, am liebsten ab Frankfurt.</em></p>' },
                    { question_text: '<p>Die Reise kostet mehr als 1.500 Euro.</p>', correct_answer: 'B',
                      explanation: '<p><strong>Falsch.</strong> Harganya 1.400 Euro, di bawah batas 1.500 Euro.</p>' },
                    { question_text: '<p>Das Frühstück ist im Preis inklusive.</p>', correct_answer: 'A',
                      explanation: '<p><strong>Richtig.</strong> <em>Frühstück ist inklusive.</em> Yang bayar terpisah adalah makan malam.</p>' }
                ]
            },
            {
                title: 'Radiosendung — Tipps für die Prüfungszeit',
                content_text: '<p><em>Sie hören eine Radiosendung. Sind die Aussagen 1–4 richtig oder falsch?</em></p><p><strong>Transkript</strong></p><p><strong>Moderator:</strong> Viele Schülerinnen und Schüler haben jetzt Prüfungen. Frau Dr. Weber, was raten Sie?</p><p><strong>Dr. Weber:</strong> Am wichtigsten ist, früh anzufangen. Wer drei Wochen vor der Prüfung beginnt, hat weniger Stress.</p><p><strong>Moderator:</strong> Und wie lange sollte man am Stück lernen?</p><p><strong>Dr. Weber:</strong> Nach etwa 45 Minuten braucht das Gehirn eine Pause. Dann am besten kurz an die frische Luft gehen.</p><p><strong>Moderator:</strong> Viele trinken beim Lernen sehr viel Kaffee …</p><p><strong>Dr. Weber:</strong> Ein, zwei Tassen sind kein Problem. Besser ist aber Wasser. Und am Abend vor der Prüfung sollte man nicht mehr lernen, sondern früh schlafen gehen.</p>',
                questions: [
                    { question_text: '<p>Man sollte etwa drei Wochen vor der Prüfung mit dem Lernen beginnen.</p>', correct_answer: 'A',
                      explanation: '<p><strong>Richtig.</strong> <em>Wer drei Wochen vor der Prüfung beginnt, hat weniger Stress.</em></p>' },
                    { question_text: '<p>Dr. Weber empfiehlt, zwei Stunden ohne Pause zu lernen.</p>', correct_answer: 'B',
                      explanation: '<p><strong>Falsch.</strong> Setelah sekitar 45 menit perlu istirahat.</p>' },
                    { question_text: '<p>Kaffee ist beim Lernen völlig verboten.</p>', correct_answer: 'B',
                      explanation: '<p><strong>Falsch.</strong> <em>Ein, zwei Tassen sind kein Problem</em> — hanya air lebih baik.</p>' },
                    { question_text: '<p>Am Abend vor der Prüfung sollte man früh schlafen gehen.</p>', correct_answer: 'A',
                      explanation: '<p><strong>Richtig.</strong> <em>… nicht mehr lernen, sondern früh schlafen gehen.</em></p>' }
                ]
            },
            {
                title: 'Durchsagen — Kaufhaus, Bahnhof, Schwimmbad, Flughafen',
                content_text: '<p><em>Sie hören vier Durchsagen. Ist die Aussage zu jeder Durchsage richtig oder falsch?</em></p><p><strong>Durchsage 1 (Kaufhaus):</strong> „Liebe Kunden, unser Restaurant im 4. Stock hat heute bis 19 Uhr geöffnet. Probieren Sie unser Tagesgericht: Gemüselasagne für 7,90 Euro.“</p><p><strong>Durchsage 2 (Bahnhof):</strong> „Der ICE nach Köln, planmäßige Abfahrt 9:15 Uhr, fährt heute von Gleis 12 statt von Gleis 8.“</p><p><strong>Durchsage 3 (Schwimmbad):</strong> „Liebe Badegäste, das Schwimmbad schließt heute wegen einer Veranstaltung bereits um 17 Uhr. Die Sauna bleibt bis 22 Uhr geöffnet.“</p><p><strong>Durchsage 4 (Flughafen):</strong> „Passagiere des Fluges nach Rom werden gebeten, ihr Handgepäck zu wiegen. Erlaubt sind maximal 8 Kilogramm.“</p>',
                questions: [
                    { question_text: '<p><strong>Durchsage 1:</strong> Das Restaurant ist im Erdgeschoss.</p>', correct_answer: 'B',
                      explanation: '<p><strong>Falsch.</strong> Restorannya di <em>4. Stock</em> (lantai 4).</p>' },
                    { question_text: '<p><strong>Durchsage 2:</strong> Der Zug nach Köln fährt heute von einem anderen Gleis ab.</p>', correct_answer: 'A',
                      explanation: '<p><strong>Richtig.</strong> <em>… von Gleis 12 statt von Gleis 8</em>.</p>' },
                    { question_text: '<p><strong>Durchsage 3:</strong> Die Sauna schließt heute um 17 Uhr.</p>', correct_answer: 'B',
                      explanation: '<p><strong>Falsch.</strong> Yang tutup pukul 17 adalah kolam renang; sauna buka sampai 22.</p>' },
                    { question_text: '<p><strong>Durchsage 4:</strong> Das Handgepäck darf höchstens 8 Kilo wiegen.</p>', correct_answer: 'A',
                      explanation: '<p><strong>Richtig.</strong> <em>Erlaubt sind maximal 8 Kilogramm.</em></p>' }
                ]
            }
        ],
        cloze: [
            {
                title: 'Notizen — Termin beim Zahnarzt',
                content_text: '<p><em>Sie hören eine Nachricht auf dem Anrufbeantworter und machen Notizen. Ergänzen Sie die Lücken 1–5.</em></p><p><strong>Transkript</strong> <em>(ganti dengan audio bila sudah tersedia)</em>: „Guten Tag, hier ist die Zahnarztpraxis Dr. Becker. Ihr Termin ist am Dienstag, den 14. Mai, um 15:30 Uhr. Bitte bringen Sie Ihre Versichertenkarte mit und kommen Sie zehn Minuten früher. Falls Sie nicht kommen können, rufen Sie uns bitte unter 089 445 210 an.“</p><p><strong>Notizen</strong></p><p>Termin beim Zahnarzt am <strong>[1]</strong>, den 14. Mai, um <strong>[2]</strong> Uhr.<br>Mitbringen: <strong>[3]</strong>.<br>Ich soll <strong>[4]</strong> Minuten früher kommen.<br>Absagen unter der Nummer <strong>[5]</strong>.</p>',
                questions: [
                    { gap_no: 1, option_a: 'Montag', option_b: 'Dienstag', option_c: 'Donnerstag', option_d: 'Freitag', correct_answer: 'B',
                      explanation: '<p><strong>B — Dienstag.</strong> <em>Ihr Termin ist am Dienstag, den 14. Mai.</em></p>' },
                    { gap_no: 2, option_a: '13:30', option_b: '15:00', option_c: '15:30', option_d: '16:30', correct_answer: 'C',
                      explanation: '<p><strong>C — 15:30.</strong> <em>… um 15:30 Uhr.</em></p>' },
                    { gap_no: 3, option_a: 'den Personalausweis', option_b: 'die Versichertenkarte', option_c: 'ein Passfoto', option_d: 'Bargeld', correct_answer: 'B',
                      explanation: '<p><strong>B.</strong> <em>Bitte bringen Sie Ihre Versichertenkarte mit</em> (kartu asuransi).</p>' },
                    { gap_no: 4, option_a: 'fünf', option_b: 'zehn', option_c: 'fünfzehn', option_d: 'zwanzig', correct_answer: 'B',
                      explanation: '<p><strong>B — zehn.</strong> <em>… kommen Sie zehn Minuten früher.</em></p>' },
                    { gap_no: 5, option_a: '089 445 210', option_b: '089 454 210', option_c: '089 445 120', option_d: '089 544 210', correct_answer: 'A',
                      explanation: '<p><strong>A — 089 445 210.</strong> Perhatikan urutan angka; opsi lain menukar digit.</p>' }
                ]
            },
            {
                title: 'Notizen — Stadtführung in Heidelberg',
                content_text: '<p><em>Sie hören eine Information bei einer Stadtführung und machen Notizen. Ergänzen Sie die Lücken 1–5.</em></p><p><strong>Transkript</strong> <em>(ganti dengan audio bila sudah tersedia)</em>: „Willkommen zur Stadtführung durch Heidelberg! Unsere Tour dauert ungefähr zwei Stunden. Wir beginnen am Marktplatz und gehen dann zum Schloss. Dort machen wir um 11 Uhr eine Pause von 20 Minuten. Bitte bleiben Sie in der Gruppe. Die Tour endet an der Alten Brücke.“</p><p><strong>Notizen</strong></p><p>Dauer: ungefähr <strong>[1]</strong> Stunden.<br>Start: <strong>[2]</strong>.<br>Pause am Schloss um <strong>[3]</strong> Uhr.<br>Die Pause dauert <strong>[4]</strong> Minuten.<br>Ende: <strong>[5]</strong>.</p>',
                questions: [
                    { gap_no: 1, option_a: 'eine', option_b: 'zwei', option_c: 'drei', option_d: 'vier', correct_answer: 'B',
                      explanation: '<p><strong>B — zwei.</strong> <em>Unsere Tour dauert ungefähr zwei Stunden.</em></p>' },
                    { gap_no: 2, option_a: 'am Bahnhof', option_b: 'am Marktplatz', option_c: 'am Schloss', option_d: 'an der Alten Brücke', correct_answer: 'B',
                      explanation: '<p><strong>B.</strong> <em>Wir beginnen am Marktplatz.</em></p>' },
                    { gap_no: 3, option_a: '10', option_b: '11', option_c: '12', option_d: '13', correct_answer: 'B',
                      explanation: '<p><strong>B — 11.</strong> <em>Dort machen wir um 11 Uhr eine Pause.</em></p>' },
                    { gap_no: 4, option_a: '10', option_b: '15', option_c: '20', option_d: '30', correct_answer: 'C',
                      explanation: '<p><strong>C — 20.</strong> <em>… eine Pause von 20 Minuten.</em></p>' },
                    { gap_no: 5, option_a: 'am Marktplatz', option_b: 'am Schloss', option_c: 'an der Alten Brücke', option_d: 'am Bahnhof', correct_answer: 'C',
                      explanation: '<p><strong>C.</strong> <em>Die Tour endet an der Alten Brücke.</em></p>' }
                ]
            },
            {
                title: 'Notizen — Informationen zum Deutschkurs',
                content_text: '<p><em>Sie hören eine Information zu einem Kurs und machen Notizen. Ergänzen Sie die Lücken 1–5.</em></p><p><strong>Transkript</strong> <em>(ganti dengan audio bila sudah tersedia)</em>: „Hallo zusammen, hier noch einmal die Informationen zum Deutschkurs: Der Kurs beginnt am 3. September und findet immer montags und mittwochs von 18 bis 20 Uhr statt. Der Unterricht ist im Raum 204 im zweiten Stock. Das Kursbuch kostet 25 Euro, Sie können es in der ersten Stunde kaufen.“</p><p><strong>Notizen</strong></p><p>Kursbeginn: <strong>[1]</strong> September.<br>Kurstage: Montag und <strong>[2]</strong>.<br>Uhrzeit: 18 bis <strong>[3]</strong> Uhr.<br>Raum: <strong>[4]</strong>.<br>Kursbuch: <strong>[5]</strong> Euro.</p>',
                questions: [
                    { gap_no: 1, option_a: '3.', option_b: '13.', option_c: '23.', option_d: '30.', correct_answer: 'A',
                      explanation: '<p><strong>A — 3.</strong> <em>Der Kurs beginnt am 3. September.</em></p>' },
                    { gap_no: 2, option_a: 'Dienstag', option_b: 'Mittwoch', option_c: 'Donnerstag', option_d: 'Freitag', correct_answer: 'B',
                      explanation: '<p><strong>B.</strong> <em>… immer montags und mittwochs.</em></p>' },
                    { gap_no: 3, option_a: '19', option_b: '20', option_c: '21', option_d: '22', correct_answer: 'B',
                      explanation: '<p><strong>B — 20.</strong> <em>… von 18 bis 20 Uhr.</em></p>' },
                    { gap_no: 4, option_a: '104', option_b: '204', option_c: '240', option_d: '402', correct_answer: 'B',
                      explanation: '<p><strong>B — 204.</strong> <em>Der Unterricht ist im Raum 204.</em></p>' },
                    { gap_no: 5, option_a: '15', option_b: '20', option_c: '25', option_d: '35', correct_answer: 'C',
                      explanation: '<p><strong>C — 25.</strong> <em>Das Kursbuch kostet 25 Euro.</em></p>' }
                ]
            }
        ]
    },

    LESEN: {
        rf_single: [
            {
                question_text: '<p><em>Lesen Sie den Aushang im Treppenhaus.</em></p><p>„Liebe Mieterinnen und Mieter, am Donnerstag, 12. Oktober, wird zwischen 8 und 12 Uhr das Wasser abgestellt. Bitte stellen Sie sich rechtzeitig Wasser bereit. Ihre Hausverwaltung“</p><p><strong>Am 12. Oktober gibt es den ganzen Tag kein Wasser.</strong></p>',
                correct_answer: 'B',
                explanation: '<p><strong>Falsch.</strong> Air hanya dimatikan <em>zwischen 8 und 12 Uhr</em>, bukan seharian.</p>'
            },
            {
                question_text: '<p><em>Lesen Sie die Anzeige.</em></p><p>„Zu verschenken: gut erhaltenes Kinderbett mit Matratze. Nur Abholung, am besten am Wochenende. Tel. 0151 778 902“</p><p><strong>Das Kinderbett kostet nichts.</strong></p>',
                correct_answer: 'A',
                explanation: '<p><strong>Richtig.</strong> <em>Zu verschenken</em> = diberikan gratis.</p>'
            },
            {
                question_text: '<p><em>Lesen Sie die Nachricht.</em></p><p>„Hallo Max, ich kann morgen leider nicht zum Fußballtraining kommen, weil ich zum Arzt muss. Kannst du dem Trainer Bescheid sagen? Danke, Paul“</p><p><strong>Paul bittet Max, den Trainer zu informieren.</strong></p>',
                correct_answer: 'A',
                explanation: '<p><strong>Richtig.</strong> <em>Kannst du dem Trainer Bescheid sagen?</em> = tolong beri tahu pelatih.</p>'
            }
        ],
        rf_grouped: [
            {
                title: 'Zeitungsartikel — Fahrradstadt Münster',
                content_text: '<p><em>Lesen Sie den Text. Sind die Aussagen 1–4 richtig oder falsch?</em></p><p>Münster gilt als die Fahrradhauptstadt Deutschlands. In der Stadt gibt es mehr Fahrräder als Einwohner: Rund 320.000 Menschen leben dort, aber es gibt etwa 500.000 Fahrräder. Fast 40 Prozent aller Wege werden mit dem Rad zurückgelegt.</p><p>Besonders beliebt ist die „Promenade“, ein 4,5 Kilometer langer Ring um die Altstadt, auf dem Autos nicht fahren dürfen. Am Hauptbahnhof steht außerdem eines der größten Fahrradparkhäuser Deutschlands mit über 3.000 Plätzen.</p><p>Doch so viele Fahrräder bringen auch Probleme: Abends sind die Parkplätze oft voll, und jedes Jahr werden tausende Räder gestohlen. Die Stadt plant deshalb neue Parkplätze und mehr Kontrollen.</p>',
                questions: [
                    { question_text: '<p>In Münster gibt es mehr Fahrräder als Einwohner.</p>', correct_answer: 'A',
                      explanation: '<p><strong>Richtig.</strong> Sekitar 500.000 sepeda untuk 320.000 penduduk.</p>' },
                    { question_text: '<p>Auf der Promenade dürfen auch Autos fahren.</p>', correct_answer: 'B',
                      explanation: '<p><strong>Falsch.</strong> <em>… auf dem Autos nicht fahren dürfen.</em></p>' },
                    { question_text: '<p>Das Fahrradparkhaus am Bahnhof hat weniger als 1.000 Plätze.</p>', correct_answer: 'B',
                      explanation: '<p><strong>Falsch.</strong> Tempat parkirnya <em>über 3.000 Plätze</em>.</p>' },
                    { question_text: '<p>Fahrraddiebstahl ist in Münster ein Problem.</p>', correct_answer: 'A',
                      explanation: '<p><strong>Richtig.</strong> <em>… jedes Jahr werden tausende Räder gestohlen.</em></p>' }
                ]
            },
            {
                title: 'E-Mail — Einladung zum Sommerfest',
                content_text: '<p><em>Lesen Sie die E-Mail. Sind die Aussagen 1–4 richtig oder falsch?</em></p><p>Liebe Kolleginnen und Kollegen,</p><p>am Freitag, den 21. Juni, feiern wir unser jährliches Sommerfest im Garten hinter dem Bürogebäude. Los geht es um 16 Uhr, die Arbeit endet an diesem Tag deshalb schon um 15 Uhr.</p><p>Für Essen und Getränke sorgt die Firma. Wer möchte, kann gern einen Salat oder einen Kuchen mitbringen. Partner und Kinder sind herzlich willkommen.</p><p>Bitte meldet euch bis zum 14. Juni bei mir an, damit wir genug Essen bestellen können. Bei Regen feiern wir in der Kantine.</p><p>Viele Grüße<br>Katrin Vogel (Personalabteilung)</p>',
                questions: [
                    { question_text: '<p>Am 21. Juni arbeiten die Mitarbeiter nur bis 15 Uhr.</p>', correct_answer: 'A',
                      explanation: '<p><strong>Richtig.</strong> <em>… die Arbeit endet an diesem Tag deshalb schon um 15 Uhr.</em></p>' },
                    { question_text: '<p>Jeder Mitarbeiter muss Essen mitbringen.</p>', correct_answer: 'B',
                      explanation: '<p><strong>Falsch.</strong> Makanan disediakan perusahaan; membawa salad/kue hanya opsional (<em>wer möchte</em>).</p>' },
                    { question_text: '<p>Familienmitglieder dürfen nicht zum Fest kommen.</p>', correct_answer: 'B',
                      explanation: '<p><strong>Falsch.</strong> <em>Partner und Kinder sind herzlich willkommen.</em></p>' },
                    { question_text: '<p>Wenn es regnet, findet das Fest in der Kantine statt.</p>', correct_answer: 'A',
                      explanation: '<p><strong>Richtig.</strong> <em>Bei Regen feiern wir in der Kantine.</em></p>' }
                ]
            },
            {
                title: 'Hausordnung — Jugendherberge Bergblick',
                content_text: '<p><em>Lesen Sie die Hausordnung. Sind die Aussagen 1–4 richtig oder falsch?</em></p><p><strong>Hausordnung – Jugendherberge Bergblick</strong></p><p>Die Rezeption ist täglich von 7 bis 22 Uhr geöffnet. Wer später ankommt, bekommt den Zimmerschlüssel aus dem Schlüsselkasten am Eingang.</p><p>Frühstück gibt es von 7:00 bis 9:30 Uhr im Speisesaal. Lunchpakete für Ausflüge können am Vorabend bis 20 Uhr bestellt werden.</p><p>Ab 22 Uhr ist Nachtruhe. Rauchen ist im ganzen Haus verboten, auf der Terrasse aber erlaubt. Am Abreisetag müssen die Zimmer bis 10 Uhr frei sein.</p>',
                questions: [
                    { question_text: '<p>Die Rezeption ist rund um die Uhr geöffnet.</p>', correct_answer: 'B',
                      explanation: '<p><strong>Falsch.</strong> Resepsionis buka <em>von 7 bis 22 Uhr</em>, bukan 24 jam.</p>' },
                    { question_text: '<p>Lunchpakete muss man am Abend vorher bestellen.</p>', correct_answer: 'A',
                      explanation: '<p><strong>Richtig.</strong> <em>… können am Vorabend bis 20 Uhr bestellt werden.</em></p>' },
                    { question_text: '<p>Auf der Terrasse darf man rauchen.</p>', correct_answer: 'A',
                      explanation: '<p><strong>Richtig.</strong> <em>… auf der Terrasse aber erlaubt.</em></p>' },
                    { question_text: '<p>Am Abreisetag kann man bis 12 Uhr im Zimmer bleiben.</p>', correct_answer: 'B',
                      explanation: '<p><strong>Falsch.</strong> Kamar harus kosong <em>bis 10 Uhr</em>.</p>' }
                ]
            }
        ],
        cloze: [
            {
                title: 'Lückentext — E-Mail an Jana',
                content_text: '<p><em>Lesen Sie die E-Mail und wählen Sie für jede Lücke 1–5 die richtige Lösung.</em></p><p>Liebe Jana,</p><p>vielen Dank <strong>[1]</strong> deine Einladung! Ich komme sehr gern zu deiner Geburtstagsparty. Leider kann ich erst um 21 Uhr da sein, <strong>[2]</strong> ich bis 20 Uhr arbeiten muss. Soll ich etwas mitbringen? Ich könnte einen Kuchen backen, <strong>[3]</strong> du möchtest. Ich freue mich schon sehr, <strong>[4]</strong> wiederzusehen. Hoffentlich ist das Wetter schön, dann <strong>[5]</strong> wir im Garten feiern.</p><p>Liebe Grüße<br>Lena</p>',
                questions: [
                    { gap_no: 1, option_a: 'für', option_b: 'über', option_c: 'an', option_d: 'auf', correct_answer: 'A',
                      explanation: '<p><strong>A — für.</strong> Ungkapan tetap: <em>Danke für + Akkusativ</em>.</p>' },
                    { gap_no: 2, option_a: 'weil', option_b: 'deshalb', option_c: 'trotzdem', option_d: 'obwohl', correct_answer: 'A',
                      explanation: '<p><strong>A — weil.</strong> Alasan dengan verba di akhir (<em>… arbeiten muss</em>). <em>obwohl</em> bermakna kontras, tidak cocok.</p>' },
                    { gap_no: 3, option_a: 'wenn', option_b: 'als', option_c: 'ob', option_d: 'dass', correct_answer: 'A',
                      explanation: '<p><strong>A — wenn.</strong> Syarat: <em>kalau kamu mau</em>.</p>' },
                    { gap_no: 4, option_a: 'dich', option_b: 'dir', option_c: 'du', option_d: 'dein', correct_answer: 'A',
                      explanation: '<p><strong>A — dich.</strong> <em>jemanden wiedersehen</em> memerlukan Akkusativ.</p>' },
                    { gap_no: 5, option_a: 'können', option_b: 'kannst', option_c: 'kann', option_d: 'könnt', correct_answer: 'A',
                      explanation: '<p><strong>A — können.</strong> Subjek <em>wir</em> → <em>wir können</em>.</p>' }
                ]
            },
            {
                title: 'Lückentext — Mitteilung der Sprachschule',
                content_text: '<p><em>Lesen Sie die Mitteilung und wählen Sie für jede Lücke 1–5 die richtige Lösung.</em></p><p>Sehr geehrte Kursteilnehmerinnen und Kursteilnehmer,</p><p>ab nächster Woche findet der Kurs nicht mehr im Raum 12, <strong>[1]</strong> im Raum 25 statt. Der Raum ist größer und hat <strong>[2]</strong> moderne Technik. Bitte denken Sie daran, Ihre Hausaufgaben <strong>[3]</strong> Montag abzugeben. Wer krank ist, <strong>[4]</strong> sich bitte telefonisch im Sekretariat abmelden. Bei Fragen stehen wir Ihnen gern <strong>[5]</strong> Verfügung.</p><p>Mit freundlichen Grüßen<br>Ihre Sprachschule</p>',
                questions: [
                    { gap_no: 1, option_a: 'sondern', option_b: 'aber', option_c: 'oder', option_d: 'denn', correct_answer: 'A',
                      explanation: '<p><strong>A — sondern.</strong> Setelah negasi (<em>nicht mehr …</em>) koreksinya memakai <em>sondern</em>.</p>' },
                    { gap_no: 2, option_a: 'eine', option_b: 'einen', option_c: 'einem', option_d: 'einer', correct_answer: 'A',
                      explanation: '<p><strong>A — eine.</strong> <em>die Technik</em> (feminin), Akkusativ setelah <em>hat</em> → <em>eine</em>.</p>' },
                    { gap_no: 3, option_a: 'bis', option_b: 'seit', option_c: 'um', option_d: 'ab', correct_answer: 'A',
                      explanation: '<p><strong>A — bis.</strong> Batas waktu: <em>bis Montag</em>.</p>' },
                    { gap_no: 4, option_a: 'soll', option_b: 'sollen', option_c: 'sollst', option_d: 'sollt', correct_answer: 'A',
                      explanation: '<p><strong>A — soll.</strong> <em>Wer …</em> diikuti verba orang ketiga tunggal.</p>' },
                    { gap_no: 5, option_a: 'zur', option_b: 'zum', option_c: 'zu', option_d: 'bei', correct_answer: 'A',
                      explanation: '<p><strong>A — zur.</strong> Ungkapan tetap: <em>zur Verfügung stehen</em>.</p>' }
                ]
            },
            {
                title: 'Lückentext — Blog: Mein Umzug nach Hamburg',
                content_text: '<p><em>Lesen Sie den Blogbeitrag und wählen Sie für jede Lücke 1–5 die richtige Lösung.</em></p><p>Vor zwei Monaten bin ich nach Hamburg <strong>[1]</strong>. Am Anfang war alles neu und ich kannte niemanden. <strong>[2]</strong> habe ich mich in einem Sportverein angemeldet. Dort habe ich schnell nette Leute kennengelernt, mit <strong>[3]</strong> ich jetzt oft am Wochenende etwas unternehme. Die Stadt gefällt mir sehr, <strong>[4]</strong> die Mieten sind leider ziemlich hoch. Ich wohne in einer kleinen Wohnung, <strong>[5]</strong> nur zehn Minuten vom Hafen entfernt ist.</p>',
                questions: [
                    { gap_no: 1, option_a: 'gezogen', option_b: 'gezieht', option_c: 'ziehen', option_d: 'gezogt', correct_answer: 'A',
                      explanation: '<p><strong>A — gezogen.</strong> Partizip II dari <em>ziehen</em> adalah <em>gezogen</em> (Perfekt dengan <em>sein</em>).</p>' },
                    { gap_no: 2, option_a: 'Deshalb', option_b: 'Weil', option_c: 'Obwohl', option_d: 'Damit', correct_answer: 'A',
                      explanation: '<p><strong>A — Deshalb.</strong> Diikuti verba di posisi 2 (<em>Deshalb habe ich …</em>); <em>weil/obwohl/damit</em> butuh verba di akhir.</p>' },
                    { gap_no: 3, option_a: 'denen', option_b: 'die', option_c: 'der', option_d: 'den', correct_answer: 'A',
                      explanation: '<p><strong>A — denen.</strong> Pronomen relatif Dativ Plural setelah <em>mit</em> (<em>Leute</em> jamak).</p>' },
                    { gap_no: 4, option_a: 'aber', option_b: 'sondern', option_c: 'deshalb', option_d: 'weil', correct_answer: 'A',
                      explanation: '<p><strong>A — aber.</strong> Kontras tanpa negasi sebelumnya; susunan kata tetap (<em>die Mieten sind</em>).</p>' },
                    { gap_no: 5, option_a: 'die', option_b: 'der', option_c: 'das', option_d: 'den', correct_answer: 'A',
                      explanation: '<p><strong>A — die.</strong> Merujuk ke <em>die Wohnung</em> (feminin), Nominativ dalam anak kalimat relatif.</p>' }
                ]
            }
        ]
    },

    SCHREIBEN: {
        cloze: [
            {
                title: 'Lückentext — Formelle Anfrage an eine Sprachschule',
                content_text: '<p><em>Ergänzen Sie die formelle E-Mail. Wählen Sie für jede Lücke 1–5 die passende Formulierung.</em></p><p><strong>[1]</strong> Damen und Herren,</p><p>ich interessiere mich für Ihren Deutschkurs auf Niveau B1 und hätte einige Fragen. <strong>[2]</strong> Sie mir bitte mitteilen, wann der nächste Kurs beginnt? Außerdem möchte ich wissen, <strong>[3]</strong> der Kurs kostet. Ich arbeite tagsüber, <strong>[4]</strong> wäre ein Abendkurs für mich ideal.</p><p>Ich freue mich auf Ihre Antwort.</p><p><strong>[5]</strong><br>Ahmad Karimi</p>',
                questions: [
                    { gap_no: 1, option_a: 'Sehr geehrte', option_b: 'Liebe', option_c: 'Hallo', option_d: 'Sehr geehrter', correct_answer: 'A',
                      explanation: '<p><strong>A — Sehr geehrte.</strong> Salam formal standar; <em>Damen und Herren</em> jamak → <em>geehrte</em>.</p>' },
                    { gap_no: 2, option_a: 'Könnten', option_b: 'Konntet', option_c: 'Kannst', option_d: 'Könntest', correct_answer: 'A',
                      explanation: '<p><strong>A — Könnten.</strong> Permintaan sopan dengan <em>Sie</em>: <em>Könnten Sie …?</em></p>' },
                    { gap_no: 3, option_a: 'wie viel', option_b: 'wie viele', option_c: 'wann', option_d: 'wo', correct_answer: 'A',
                      explanation: '<p><strong>A — wie viel.</strong> Menanyakan harga (tak terhitung): <em>wie viel kostet …</em>.</p>' },
                    { gap_no: 4, option_a: 'deshalb', option_b: 'weil', option_c: 'obwohl', option_d: 'trotzdem', correct_answer: 'A',
                      explanation: '<p><strong>A — deshalb.</strong> Akibat + verba posisi 2 (<em>deshalb wäre …</em>).</p>' },
                    { gap_no: 5, option_a: 'Mit freundlichen Grüßen', option_b: 'Liebe Grüße', option_c: 'Tschüss', option_d: 'Bis bald', correct_answer: 'A',
                      explanation: '<p><strong>A.</strong> Penutup formal standar; yang lain informal.</p>' }
                ]
            },
            {
                title: 'Lückentext — Informelle E-Mail an Tom',
                content_text: '<p><em>Ergänzen Sie die informelle E-Mail. Wählen Sie für jede Lücke 1–5 die passende Formulierung.</em></p><p><strong>[1]</strong> Tom,</p><p>danke für deine Nachricht! Am Samstag kann ich leider nicht mit ins Kino kommen, <strong>[2]</strong> meine Eltern zu Besuch kommen. <strong>[3]</strong> du am Sonntag Zeit? Wir <strong>[4]</strong> zusammen frühstücken und danach in den Park gehen. Schreib mir einfach, wann es dir passt.</p><p><strong>[5]</strong><br>Jonas</p>',
                questions: [
                    { gap_no: 1, option_a: 'Lieber', option_b: 'Liebe', option_c: 'Sehr geehrter', option_d: 'Hallo Herr', correct_answer: 'A',
                      explanation: '<p><strong>A — Lieber.</strong> Salam informal untuk laki-laki: <em>Lieber Tom</em>.</p>' },
                    { gap_no: 2, option_a: 'weil', option_b: 'denn', option_c: 'deshalb', option_d: 'trotzdem', correct_answer: 'A',
                      explanation: '<p><strong>A — weil.</strong> Verba di akhir (<em>… zu Besuch kommen</em>). <em>denn</em> butuh verba di posisi 2.</p>' },
                    { gap_no: 3, option_a: 'Hast', option_b: 'Hat', option_c: 'Habt', option_d: 'Haben', correct_answer: 'A',
                      explanation: '<p><strong>A — Hast.</strong> Subjek <em>du</em> → <em>hast</em>.</p>' },
                    { gap_no: 4, option_a: 'könnten', option_b: 'könnte', option_c: 'könntest', option_d: 'könnt', correct_answer: 'A',
                      explanation: '<p><strong>A — könnten.</strong> Usulan sopan dengan subjek <em>wir</em>.</p>' },
                    { gap_no: 5, option_a: 'Viele Grüße', option_b: 'Hochachtungsvoll', option_c: 'Mit freundlichen Grüßen', option_d: 'Sehr geehrte Grüße', correct_answer: 'A',
                      explanation: '<p><strong>A — Viele Grüße.</strong> Penutup informal; B dan C terlalu formal, D tidak lazim.</p>' }
                ]
            },
            {
                title: 'Lückentext — Forumsbeitrag: Handy im Urlaub',
                content_text: '<p><em>Ergänzen Sie den Forumsbeitrag. Wählen Sie für jede Lücke 1–5 die passende Formulierung.</em></p><p><strong>Thema: Sollte man im Urlaub das Handy ausschalten?</strong></p><p><strong>[1]</strong> Meinung nach ist es gut, im Urlaub weniger am Handy zu sein. Man kann sich besser erholen <strong>[2]</strong> hat mehr Zeit für die Familie. <strong>[3]</strong> der anderen Seite braucht man das Handy manchmal, zum Beispiel für Karten oder Tickets. Ich schalte es deshalb nicht ganz aus, schaue <strong>[4]</strong> nur zweimal am Tag auf meine Nachrichten. <strong>[5]</strong> finde ich, dass jeder selbst entscheiden sollte.</p>',
                questions: [
                    { gap_no: 1, option_a: 'Meiner', option_b: 'Mein', option_c: 'Meine', option_d: 'Meinem', correct_answer: 'A',
                      explanation: '<p><strong>A — Meiner.</strong> Ungkapan tetap: <em>Meiner Meinung nach</em> (Dativ feminin).</p>' },
                    { gap_no: 2, option_a: 'und', option_b: 'aber', option_c: 'oder', option_d: 'denn', correct_answer: 'A',
                      explanation: '<p><strong>A — und.</strong> Menambahkan keuntungan kedua.</p>' },
                    { gap_no: 3, option_a: 'Auf', option_b: 'An', option_c: 'Von', option_d: 'In', correct_answer: 'A',
                      explanation: '<p><strong>A — Auf.</strong> Ungkapan tetap untuk argumen lawan: <em>auf der anderen Seite</em>.</p>' },
                    { gap_no: 4, option_a: 'aber', option_b: 'sondern', option_c: 'denn', option_d: 'oder', correct_answer: 'A',
                      explanation: '<p><strong>A — aber.</strong> <em>schaue aber nur …</em> = namun hanya melihat; <em>sondern</em> tidak bisa di posisi ini.</p>' },
                    { gap_no: 5, option_a: 'Zusammenfassend', option_b: 'Erstens', option_c: 'Zum Beispiel', option_d: 'Am Anfang', correct_answer: 'A',
                      explanation: '<p><strong>A — Zusammenfassend.</strong> Kata penutup untuk merangkum pendapat.</p>' }
                ]
            }
        ]
    }
};

// ════════════════════════════════════════════════════════════════════════════
// Lückentext varian cara menjawab:
//   cloze_select → dropdown inline di teks (data = MC: option_a–d + correct_answer)
//   cloze_input  → ketik jawaban (data: gap_no + answer_text + explanation, TANPA opsi)
// ════════════════════════════════════════════════════════════════════════════
const CLOZE_MODE_DUMPS = {

    HOEREN: {
        cloze_select: [
            {
                title: 'Durchsage am Bahnhof — Pilihan di Teks',
                content_text: '<p><em>Sie hören eine Durchsage am Bahnhof und ergänzen die Lücken 1–3.</em></p><p><strong>Transkript</strong> <em>(ganti dengan audio bila sudah tersedia)</em>: „Achtung an Gleis 5: Der ICE 578 nach Hamburg, planmäßige Abfahrt <strong>[1]</strong> Uhr, fährt heute mit circa 20 Minuten Verspätung ab. Bitte beachten Sie auch, dass der Regionalzug nach Nürnberg heute von Gleis <strong>[2]</strong> abfährt. Wir bitten um <strong>[3]</strong>.“</p>',
                questions: [
                    { gap_no: 1, option_a: '14:12', option_b: '14:32', option_c: '14:52', option_d: '15:32', correct_answer: 'B',
                      explanation: '<p><strong>B — 14:32.</strong> <em>planmäßige Abfahrt 14:32 Uhr</em> = jadwal normal; 14:52 adalah setelah tertunda 20 menit.</p>' },
                    { gap_no: 2, option_a: '3', option_b: '5', option_c: '8', option_d: '12', correct_answer: 'A',
                      explanation: '<p><strong>A — 3.</strong> Pemilihan kata <em>von Gleis 3</em> di transkrip.</p>' },
                    { gap_no: 3, option_a: 'Verständnis', option_b: 'Geduld', option_c: 'Hilfe', option_d: 'Bezahlung', correct_answer: 'A',
                      explanation: '<p><strong>A — Verständnis.</strong> <em>Wir bitten um Verständnis</em> = ungkapan standar pengumuman.</p>' }
                ]
            }
        ],
        cloze_input: [
            {
                title: 'Notizen — Termin beim Zahnarzt (Ketik Jawaban)',
                content_text: '<p><em>Sie hören eine Nachricht auf dem Anrufbeantworter und machen Notizen. Ergänzen Sie die Lücken 1–4.</em></p><p><strong>Transkript</strong> <em>(ganti dengan audio bila sudah tersedia)</em>: „Guten Tag, hier ist die Zahnarztpraxis Dr. Becker. Ihr Termin ist am Dienstag, den 14. Mai, um 15:30 Uhr. Bitte bringen Sie Ihre Versichertenkarte mit und kommen Sie zehn Minuten früher.“</p><p><strong>Notizen</strong></p><p>Termin am <strong>[1]</strong>, den 14. Mai, um <strong>[2]</strong> Uhr.<br>Mitbringen: <strong>[3]</strong>.<br>Ich soll <strong>[4]</strong> Minuten früher kommen.</p>',
                questions: [
                    { gap_no: 1, answer_text: 'Dienstag',
                      explanation: '<p><strong>Dienstag.</strong> <em>Ihr Termin ist am Dienstag, den 14. Mai.</em></p>' },
                    { gap_no: 2, answer_text: '15:30 Uhr',
                      explanation: '<p><strong>15:30.</strong> <em>… um 15:30 Uhr.</em> Format jam Jerman boleh 15.30 atau 15:30.</p>' },
                    { gap_no: 3, answer_text: 'Versichertenkarte',
                      explanation: '<p><strong>Versichertenkarte.</strong> <em>Bitte bringen Sie Ihre Versichertenkarte mit</em> (kartu asuransi).</p>' },
                    { gap_no: 4, answer_text: 'zehn',
                      explanation: '<p><strong>zehn.</strong> <em>… kommen Sie zehn Minuten früher.</em></p>' }
                ]
            },
            {
                title: 'Notizen — Deutschkurs (Ketik Jawaban)',
                content_text: '<p><em>Sie hören eine Information zu einem Deutschkurs und machen Notizen. Ergänzen Sie die Lücken 1–4.</em></p><p><strong>Transkript</strong> <em>(ganti dengan audio bila sudah tersedia)</em>: „Hallo zusammen, der Deutschkurs beginnt am 3. September und findet immer montags und mittwochs von 18 bis 20 Uhr statt. Der Unterricht ist im Raum 204 im zweiten Stock. Das Kursbuch kostet 25 Euro.“</p><p><strong>Notizen</strong></p><p>Kursbeginn: <strong>[1]</strong> September.<br>Kurstage: Montag und <strong>[2]</strong>.<br>Raum: <strong>[3]</strong>.<br>Kursbuch: <strong>[4]</strong> Euro.</p>',
                questions: [
                    { gap_no: 1, answer_text: '3.',
                      explanation: '<p><strong>3.</strong> <em>Der Kurs beginnt am 3. September.</em></p>' },
                    { gap_no: 2, answer_text: 'Mittwoch',
                      explanation: '<p><strong>Mittwoch.</strong> <em>… immer montags und mittwochs.</em></p>' },
                    { gap_no: 3, answer_text: '204',
                      explanation: '<p><strong>204.</strong> <em>Der Unterricht ist im Raum 204.</em></p>' },
                    { gap_no: 4, answer_text: '25',
                      explanation: '<p><strong>25.</strong> <em>Das Kursbuch kostet 25 Euro.</em></p>' }
                ]
            }
        ]
    },

    LESEN: {
        cloze_select: [
            {
                title: 'Aushang im Treppenhaus — Pilihan di Teks',
                content_text: '<p><em>Lesen Sie den Aushang und ergänzen Sie die Lücken 1–3.</em></p><p>„Liebe Mieterinnen und Mieter, am Donnerstag, 12. Oktober, wird zwischen <strong>[1]</strong> das Wasser abgestellt. Bitte stellen Sie sich rechtzeitig Wasser bereit. Bei Fragen wenden Sie sich an die Hausverwaltung, <strong>[2]</strong> 8 bis 16 Uhr. Vielen Dank für Ihr <strong>[3]</strong>. Ihre Hausverwaltung“</p>',
                questions: [
                    { gap_no: 1, option_a: '8 und 12 Uhr', option_b: '12 und 16 Uhr', option_c: '8 und 16 Uhr', option_d: 'den ganzen Tag', correct_answer: 'A',
                      explanation: '<p><strong>A.</strong> <em>zwischen 8 und 12 Uhr</em> — bukan seharian.</p>' },
                    { gap_no: 2, option_a: 'von', option_b: 'um', option_c: 'ab', option_d: 'bis', correct_answer: 'A',
                      explanation: '<p><strong>A — von.</strong> Rentang waktu: <em>von 8 bis 16 Uhr</em>.</p>' },
                    { gap_no: 3, option_a: 'Verständnis', option_b: 'Geld', option_c: 'Wasser', option_d: 'Geduld', correct_answer: 'A',
                      explanation: '<p><strong>A — Verständnis.</strong> Ungkapan standar papan pengumuman.</p>' }
                ]
            }
        ],
        cloze_input: [
            {
                title: 'Broschüre — Öffentliche Bibliothek (Ketik Jawaban)',
                content_text: '<p><em>Lesen Sie die Informationen und ergänzen Sie die Lücken 1–4.</em></p><p>Die Stadtbibliothek ist montags bis freitags von <strong>[1]</strong> bis 19 Uhr geöffnet, samstags nur bis 13 Uhr. Der Eintritt ist frei — Sie brauchen nur einen Ausweis für die Bibliotheks­karte. Pro Karte darf man maximal <strong>[2]</strong> Medien ausleihen, die Leihfrist beträgt <strong>[3]</strong> Wochen. Verspätete Rückgabe kostet pro Medium und Tag <strong>[4]</strong> Euro Gebühr.</p>',
                questions: [
                    { gap_no: 1, answer_text: '10 Uhr',
                      explanation: '<p><strong>10 Uhr.</strong> Baca lagi kalimat pertama: buka senin–jumat mulai pukul 10.</p>' },
                    { gap_no: 2, answer_text: 'zehn',
                      explanation: '<p><strong>zehn.</strong> <em>maximal zehn Medien ausleihen</em>.</p>' },
                    { gap_no: 3, answer_text: 'vier',
                      explanation: '<p><strong>vier.</strong> <em>die Leihfrist beträgt vier Wochen</em>.</p>' },
                    { gap_no: 4, answer_text: '0,50',
                      explanation: '<p><strong>0,50 Euro.</strong> Angka desimal Jerman memakai koma.</p>' }
                ]
            },
            {
                title: 'Kurzporträt — Stadt Heidelberg (Ketik Jawaban)',
                content_text: '<p><em>Lesen Sie das Kurzporträt und ergänzen Sie die Lücken 1–4.</em></p><p>Heidelberg liegt am Fluss <strong>[1]</strong> im Südwesten Deutschlands. Die Stadt hat etwa 160.000 Einwohner und ist vor allem für ihre <strong>[2]</strong> bekannt, eine der ältesten Hochschulen Europas (gegründet <strong>[3]</strong>). Berühmt ist auch das Schloss hoch über der Stadt — jedes Sommerende gibt es dort ein großes <strong>[4]</strong> mit Feuerwerk.</p>',
                questions: [
                    { gap_no: 1, answer_text: 'Neckar',
                      explanation: '<p><strong>Neckar.</strong> <em>am Fluss Neckar</em>.</p>' },
                    { gap_no: 2, answer_text: 'Universität',
                      explanation: '<p><strong>Universität.</strong> Salah satu universitas tertua di Eropa.</p>' },
                    { gap_no: 3, answer_text: '1386',
                      explanation: '<p><strong>1386.</strong> Tahun berdirinya Universitas Heidelberg.</p>' },
                    { gap_no: 4, answer_text: 'Fest',
                      explanation: '<p><strong>Fest.</strong> <em>ein großes Fest mit Feuerwerk</em>.</p>' }
                ]
            }
        ]
    },

    SCHREIBEN: {
        cloze_select: [
            {
                title: 'Formelle E-Mail — Pilihan di Teks',
                content_text: '<p><em>Ergänzen Sie die formelle E-Mail. Wählen Sie für jede Lücke 1–3.</em></p><p><strong>[1]</strong> Damen und Herren,</p><p>ich interessiere mich für Ihren Deutschkurs und hätte eine Frage: <strong>[2]</strong> Sie mir bitte mitteilen, wann der nächste Kurs beginnt? Ich arbeite tagsüber, <strong>[3]</strong> wäre ein Abendkurs ideal.</p><p>Mit freundlichen Grüßen</p>',
                questions: [
                    { gap_no: 1, option_a: 'Sehr geehrte', option_b: 'Liebe', option_c: 'Hallo', option_d: 'Sehr geehrter', correct_answer: 'A',
                      explanation: '<p><strong>A.</strong> Salam formal + <em>Damen und Herren</em> jamak.</p>' },
                    { gap_no: 2, option_a: 'Könnten', option_b: 'Konntet', option_c: 'Kannst', option_d: 'Könntest', correct_answer: 'A',
                      explanation: '<p><strong>A — Könnten.</strong> Permintaan sopan dengan <em>Sie</em>.</p>' },
                    { gap_no: 3, option_a: 'deshalb', option_b: 'weil', option_c: 'obwohl', option_d: 'trotzdem', correct_answer: 'A',
                      explanation: '<p><strong>A — deshalb.</strong> Akibat + verba posisi 2.</p>' }
                ]
            }
        ],
        cloze_input: [
            {
                title: 'Formelle E-Mail — Ketik Jawaban',
                content_text: '<p><em>Ergänzen Sie die formelle E-Mail mit einem passenden Wort.</em></p><p>Sehr geehrte Damen und Herren,</p><p>ich habe Ihre Anzeige im Internet gelesen und möchte mich um die Stelle als <strong>[1]</strong> bewerben. Zurzeit besuche ich einen Deutschkurs auf Niveau <strong>[2]</strong>. In meiner Freizeit spiele ich gern Klavier und treibe <strong>[3]</strong>.</p><p>Über eine Einladung zu einem Gespräch würde ich mich sehr <strong>[4]</strong>.</p><p>Mit freundlichen Grüßen</p>',
                questions: [
                    { gap_no: 1, answer_text: 'Verkäufer',
                      explanation: '<p>Posisi kerja yang wajar untuk lamaran — sesuai konteks iklan.</p>' },
                    { gap_no: 2, answer_text: 'B1',
                      explanation: '<p>Level bahasa umum: A1–C1 (GEFR).</p>' },
                    { gap_no: 3, answer_text: 'Sport',
                      explanation: '<p>Aktivitas olahraga yang wajar dalam <em>treibe ___</em>.</p>' },
                    { gap_no: 4, answer_text: 'freuen',
                      explanation: '<p><strong>freuen.</strong> Frasa tetap: <em>sich über etwas freuen</em>.</p>' }
                ]
            }
        ]
    }
};

function plainText(html) {
    return String(html || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
}

function dumpTitle(item, mode) {
    const title = mode === 'grouped'
        ? ((item.title || '').trim() || plainText(item.content_text))
        : plainText(item.question_text);
    return (title || 'Dump').substring(0, 80);
}

// jenis → [question_mode, answer_type, cloze_mode]; sama dengan DUMP_JENIS di app_settings_proc.py
const JENIS = {
    single      : ['single',  'mc',    ''],
    grouped     : ['grouped', 'mc',    ''],
    rf_single   : ['single',  'rf',    ''],
    rf_grouped  : ['grouped', 'rf',    ''],
    cloze       : ['grouped', 'cloze', ''],
    cloze_select: ['grouped', 'cloze', 'select'],
    cloze_input : ['grouped', 'cloze', 'input'],
};

Object.keys(EXTRA_DUMPS).forEach(function (code) {
    DUMPS[code] = Object.assign(DUMPS[code] || {}, EXTRA_DUMPS[code]);
});
Object.keys(CLOZE_MODE_DUMPS).forEach(function (code) {
    DUMPS[code] = Object.assign(DUMPS[code] || {}, CLOZE_MODE_DUMPS[code]);
});

let inserted = 0;
let skipped  = 0;

Object.keys(DUMPS).forEach(function (code) {
    if (!db.db_test_type.findOne({ code: code, is_deleted: false })) {
        print('PERINGATAN: tipe tes ' + code + ' belum ada di db_test_type — dump tetap disimpan dengan kode ini.');
    }
    Object.keys(DUMPS[code]).forEach(function (jenis) {
        const mode        = JENIS[jenis][0];
        const answerType  = JENIS[jenis][1];
        const clozeMode   = JENIS[jenis][2] || '';
        const typeQuery   = answerType === 'mc' ? { $in: ['mc', null] } : answerType;
        const clozeQuery  = clozeMode === '' ? {} : (clozeMode === 'select' || clozeMode === 'input' ? clozeMode : { $in: ['mc', null] });
        const baseQuery   = { fk_test_type_code: code, question_mode: mode, answer_type: typeQuery, is_deleted: false };
        const dedupQuery  = Object.assign({}, baseQuery, Object.keys(clozeQuery).length ? { cloze_mode: clozeQuery } : {});
        let order = db.db_test_type_dump.countDocuments(Object.assign({}, baseQuery, Object.keys(clozeQuery).length ? { cloze_mode: clozeQuery } : {}));
        (DUMPS[code][jenis] || []).forEach(function (item) {
            const title = dumpTitle(item, mode);
            if (db.db_test_type_dump.findOne(Object.assign({}, dedupQuery, { title: title }))) {
                skipped += 1;
                return;
            }
            const counterRec = db.db_unique_counter.findOneAndUpdate(
                {}, { $inc: { counter: 1 } }, { upsert: true, returnDocument: 'before' }
            );
            const counter = counterRec ? counterRec.counter : 0;
            const id = new ObjectId();
            const ts = Date.now() + 7 * 60 * 60 * 1000;
            order += 1;
            const doc = {
                _id               : id,
                ipkey             : id.toHexString(),
                pkey              : id.toHexString() + '-' + (1000 + Math.floor(Math.random() * 9000)) + '-' + counter,
                is_deleted        : false,
                rec_timestamp     : ts,
                rec_timestamp_str : new Date(ts).toISOString().replace('T', ' ').substring(0, 19),
                fk_test_type_code : code,
                question_mode     : mode,
                answer_type       : answerType,
                title             : title,
                dump_json         : JSON.stringify(item),
                sort_order        : order,
                status            : 'ACTIVE',
            };
            if (clozeMode !== '') doc.cloze_mode = clozeMode;
            db.db_test_type_dump.insertOne(doc);
            inserted += 1;
            print('inserted ' + code + ' / ' + jenis + ': ' + title);
        });
    });
});

print('\nSelesai: ' + inserted + ' dump ditambahkan, ' + skipped + ' dilewati (sudah ada).');
