from django.db import migrations


def seed_openeire_flagship_project(apps, schema_editor):
    Project = apps.get_model("portfolio", "Project")

    Project.objects.update_or_create(
        title="OpenEire Studios",
        defaults={
            "description_en": (
                "A custom Django and React platform for selling licensed drone media, "
                "managing protected galleries, and handling both digital and physical fulfilment."
            ),
            "description_ro": (
                "O platforma personalizata Django si React pentru vanzarea de media "
                "drone licentiata, gestionarea galeriilor protejate si administrarea "
                "livrarii atat pentru produse digitale, cat si fizice."
            ),
            "description_es": (
                "Una plataforma personalizada con Django y React para vender contenido "
                "aereo con licencia, gestionar galerias protegidas y coordinar la "
                "entrega de productos digitales y fisicos."
            ),
            "tech_stack": (
                "Django, Django REST Framework, React, TypeScript, PostgreSQL, "
                "Stripe, Cloudflare R2, Redis"
            ),
            "repo_link": "",
            "live_link": "",
            "featured": True,
            "client_challenge_en": (
                "OpenEire needed more than a brochure site. The platform had to support "
                "rights-managed licensing, gated digital delivery, print fulfilment, and "
                "an admin workflow that could safely handle protected media assets."
            ),
            "client_challenge_ro": (
                "OpenEire avea nevoie de mai mult decat un site de prezentare. Platforma "
                "trebuia sa sustina licentiere rights-managed, livrare digitala protejata, "
                "fulfilment pentru printuri si un flux administrativ sigur pentru active media."
            ),
            "client_challenge_es": (
                "OpenEire necesitaba mas que un sitio de presentacion. La plataforma debia "
                "cubrir licencias rights-managed, entrega digital protegida, fulfilment de "
                "impresiones y un flujo administrativo seguro para contenido multimedia."
            ),
            "my_solution_en": (
                "I designed a full-stack commerce application with Django as the business "
                "logic core and React as the client layer. The system coordinates licensing, "
                "secure asset delivery, print orders, payments, and AI-assisted admin support "
                "through one custom architecture."
            ),
            "my_solution_ro": (
                "Am proiectat o aplicatie full-stack de commerce cu Django ca nucleu al "
                "logicii de business si React ca strat de interfata. Sistemul coordoneaza "
                "licentierea, livrarea securizata a fisierelor, comenzile de print, platile "
                "si suportul administrativ asistat de AI intr-o singura arhitectura custom."
            ),
            "my_solution_es": (
                "Diseñe una aplicacion full-stack de commerce con Django como nucleo de la "
                "logica de negocio y React como capa de cliente. El sistema coordina "
                "licencias, entrega segura de archivos, pedidos de impresion, pagos y "
                "soporte administrativo asistido por IA en una sola arquitectura a medida."
            ),
            "the_result_en": (
                "OpenEire now has a platform built around its real business model instead of "
                "forcing that model into a template. It demonstrates how custom software can "
                "support protected content, complex product flows, and future growth."
            ),
            "the_result_ro": (
                "OpenEire are acum o platforma construita in jurul modelului sau real de "
                "business, nu fortata intr-un sablon. Proiectul arata cum software-ul custom "
                "poate sustine continut protejat, fluxuri complexe de produs si crestere pe termen lung."
            ),
            "the_result_es": (
                "OpenEire ahora cuenta con una plataforma construida alrededor de su modelo "
                "real de negocio, no forzada dentro de una plantilla. El proyecto demuestra "
                "como el software a medida puede sostener contenido protegido, flujos de "
                "producto complejos y crecimiento futuro."
            ),
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ("portfolio", "0025_alter_service_starting_price_and_more"),
    ]

    operations = [
        migrations.RunPython(
            seed_openeire_flagship_project,
            migrations.RunPython.noop,
        ),
    ]
