from app import create_app
from models import db, User, Topic


def seed():
    app = create_app('development')
    with app.app_context():
        db.create_all()

        # Admin (med passord — ferdig registrert)
        admin = User.query.filter_by(email='toraus11@gmail.com').first()
        if not admin:
            admin = User(
                name='Tore Ausland',
                email='toraus11@gmail.com',
                apartment='Tiger Palm A1',
                phase='Fase 1',
                is_admin=True,
                is_approved=True,
            )
            admin.set_password('RoyalPalms2026!')
            db.session.add(admin)
            db.session.flush()
            print('Admin-bruker opprettet: toraus11@gmail.com')

        # Pre-opprett deltakere fra Excel-listen (UTEN passord).
        # De fullfører registreringen selv ved å sette passord + leilighetsnavn.
        inviterte = [
            {'name': 'Patrick Sarin', 'email': 'patrik.sarin@me.com'},
            {'name': 'John Fransson', 'email': 'john.fransson@frentab.se'},
            {'name': 'Tor Håkon Solheim', 'email': 'tor-h@motornorge.no'},
            {'name': 'Henning Jensen', 'email': 'henning@incubatix.se'},
            {'name': 'Atle Hansen', 'email': 'atle.hansen@accelerate-iver.no'},
            {'name': 'Geir Viken', 'email': 'geir.viken@hotmail.com'},
            {'name': 'Lotte Wullum', 'email': 'lottewullum@hotmail.com'},
            {'name': 'Kent Schultz', 'email': 'kent_s.schultz@hotmail.com'},
            {'name': 'Jörgen Ritterstrandh', 'email': 'jorgen@nextor.se'},
            {'name': 'Laila Espenes', 'email': 'laila-espenes@hotmail.com'},
        ]

        for inv in inviterte:
            existing = User.query.filter_by(email=inv['email']).first()
            if not existing:
                user = User(
                    name=inv['name'],
                    email=inv['email'],
                    apartment='',
                    phase='Fase 1',
                    password_hash=None,  # Ingen passord — må fullføre registrering
                )
                db.session.add(user)
                print(f'  Invitert (uten passord): {inv["email"]}')

        topics_data = [
            {
                'title': 'Signering av snaggingliste — fritar dette utbygger for ansvar?',
                'description': (
                    'Analyse av om signering av ferdigbefaringsrapporten (snagging report) '
                    'fritar OneEden for ansvar for mangler. Gjennomgang av kontraktens klausul 16 '
                    'og LOE-garantier. Snaggingrapporten selv sier at signatur kun bekrefter '
                    'mottak, ikke aksept av tilstanden. Viktig å avklare med advokat: Hva bør vi '
                    'IKKE kvittere ut, og hvordan sikrer vi oss?'
                ),
            },
            {
                'title': 'LOE-garantier (1, 3 og 10 år) — omfang og beskyttelse',
                'description': (
                    'Gjennomgang av Ley de Ordenación de la Edificación (LOE, Lov 38/1999). '
                    'Lovfestede garantier: 1 år for utførelsesmangler (acabados), 3 år for '
                    'beboelighetsmangler/habitabilidad (fuktskader faller her), og 10 år for '
                    'strukturelle feil (seguro decenal). Disse garantiene kan IKKE fravikes ved '
                    'kontrakt — de gjelder uansett hva som avtales med utbygger.'
                ),
            },
            {
                'title': 'Utbedringsmetode — er perimetertetting (inyección perimetral) tilstrekkelig?',
                'description': (
                    'Teknisk vurdering av OneEdens foreslåtte utbedringsmetode (perimetertetting/'
                    'injeksjon) opp mot kravene i CTE DB HS1 «Protección frente a la humedad». '
                    'Faglitteraturen indikerer at perimetertetting alene er utilstrekkelig når '
                    'utvendig membran mangler eller er skadet. En forskriftsmessig løsning krever '
                    'utvendig membran, dreneringssystem og innvendig behandling.'
                ),
            },
            {
                'title': 'Forbehold og klausuler i skjøtet (escritura) ved overtakelse',
                'description': (
                    'Hvilke forbehold bør kjøpere ta inn i skjøtet (escritura pública) ved '
                    'overtakelse når det er utestående mangler? Viktige punkter: Vedlegg med '
                    'mangelliste, krav om CTE HS1-konform utbedring, bindende tidsfrist, '
                    'konvensjonalbot ved oversittelse, LOE-forbehold, rett til uavhengig '
                    'inspeksjon, og garanti på utbedringsarbeidet.'
                ),
            },
            {
                'title': 'Sikkerhetsmangel — verandadører som kan åpnes utenfra',
                'description': (
                    'Alvorlig sikkerhetsmangel: Verandadører i Royal Palms kan åpnes utenfra '
                    'selv når de er låst. Dette er bekreftet av minst én kjøper. Representerer '
                    'en umiddelbar sikkerhetsrisiko som påvirker beboelighet (habitabilidad) '
                    'under LOE og potensielt forsikringsdekning. Må dokumenteres av flere og '
                    'rapporteres formelt til OneEden.'
                ),
            },
            {
                'title': 'Eskaleringsplan — burofax, OMIC, Junta de Andalucía, rettslige skritt',
                'description': (
                    'Trinnvis eskaleringsplan dersom OneEden ikke responderer tilfredsstillende: '
                    '1) Formelt krav via advokat (burofax — juridisk dokumenterbart i Spania), '
                    '2) Klage til OMIC (Oficina Municipal de Información al Consumidor, Mijas), '
                    '3) Klage til Junta de Andalucía — Dirección General de Consumo, '
                    '4) Anmeldelse til byggetilsynet (Ayuntamiento de Mijas, Urbanismo), '
                    '5) Rettslige skritt (sivil rettssak basert på LOE).'
                ),
            },
            {
                'title': 'Overtakelse med utestående mangler — forbehold og risikovurdering',
                'description': (
                    'Kontraktens klausul 16.2 krever at kjøper møter til skjøtesignering selv '
                    'om utbedringer ikke er ferdige. Klausul 16.3 forplikter utbygger til å '
                    'utbedre etterpå. Analyse av risiko ved overtakelse: Hva må inn i skjøtet '
                    'for at vi er beskyttet? Kan vi trygt overta hvis riktige forbehold er på plass?'
                ),
            },
            {
                'title': 'Sameiet og ansvar for følgeskader av byggefeil etter overtakelse',
                'description': (
                    'Når sameiet (comunidad de propietarios) er etablert, overtar det ansvaret '
                    'for vedlikehold og drift av bygningsmassen. Dersom det oppstår følgeskader '
                    'som kan spores tilbake til opprinnelige byggefeil — f.eks. fuktrelaterte '
                    'skader på konstruksjon, fellesarealer eller tekniske installasjoner — '
                    'risikerer sameiet å sitte med kostnadene. Avgjørende å sikre utbyggers '
                    'ansvar FØR overtakelse.'
                ),
            },
            {
                'title': 'Felles advokat og fagkyndig — valg og mandat',
                'description': (
                    'Koordinering av valg av felles advokat (abogado) og fagkyndig '
                    '(perito/arquitecto técnico) for kjøpergruppen. Temaer: Mandat og '
                    'fullmaktsstruktur, kostnadsfordeling mellom deltakerne, utvelgelseskriterier '
                    '(spesialisering i eiendomsrett/byggerett i Andalucía), og praktisk '
                    'organisering av samarbeidet.'
                ),
            },
        ]

        for i, t in enumerate(topics_data, 1):
            existing = Topic.query.filter_by(title=t['title']).first()
            if not existing:
                topic = Topic(
                    title=t['title'],
                    description=t['description'],
                    sort_order=i,
                    status='under_diskusjon',
                    created_by_id=admin.id,
                )
                db.session.add(topic)

        db.session.commit()
        total_users = User.query.count()
        registered = User.query.filter(User.password_hash.isnot(None)).count()
        pending = total_users - registered
        print(f'Seed fullført: {total_users} brukere ({registered} registrert, {pending} venter), '
              f'{Topic.query.count()} temaer.')


if __name__ == '__main__':
    seed()
