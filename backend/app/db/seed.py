from app.core.config import settings
from app.core.security import hash_password
from app.crud import category as crud_category
from app.crud import emplacement as crud_emplacement
from app.crud import statut as crud_statut
from app.crud import user as crud_user
from app.db.session import AsyncSessionLocal
from app.models.user import User, UserRole
from app.schemas.category import CategoryCreate

DEFAULT_CATEGORIES = [
    {"nom": "Informatique", "description": "Ordinateurs, serveurs, peripheriques"},
    {"nom": "Immobilier", "description": "Equipements immobiliers, batiment et mobilier de bureau"},
    {"nom": "Nettoyage", "description": "Materiel de nettoyage et entretien"},
]

DEFAULT_STATUTS = [
    {"nom": "Fonctionnel", "description": "Operationnel et disponible"},
    {"nom": "Defectueux", "description": "Hors service"},
    {"nom": "En maintenance", "description": "Envoye en maintenance"},
]

DEFAULT_EMPLACEMENTS = [
    {"nom": "Entrepot"},
    {"nom": "Bureau"},
]

# Statuts du cycle de vie materiel (module affectations).
DEFAULT_STATUTS.extend(
    [
        {"nom": "En stock", "description": "Disponible pour affectation"},
        {"nom": "Affecte", "description": "Sous la responsabilite d'un collaborateur"},
        {"nom": "Endommage", "description": "Inutilisable en l'etat"},
        {"nom": "Perdu", "description": "Non retrouve"},
        {"nom": "Retourne", "description": "Rendu par le collaborateur"},
        {"nom": "Hors service", "description": "Retire definitivement du parc"},
    ]
)

# Catalogue materiel realiste par categorie (reference auto : PREFIX-XXX).
DEFAULT_CATALOGUE = {
    "Informatique": [
        ("Dell Latitude 5540", "Dell", "Latitude 5540", "Ordinateur portable professionnel 15\" i7/16Go/512Go SSD", 10),
        ("HP EliteBook 860 G11", "HP", "EliteBook 860 G11", "Ordinateur portable entreprise 16\" Core Ultra 7", 8),
        ("Lenovo ThinkPad L14 Gen 5", "Lenovo", "ThinkPad L14 Gen 5", "Ordinateur portable 14\" Ryzen 7", 6),
        ("Apple iMac 24 M3", "Apple", "iMac 24 M3", "Poste tout-en-un 24\" puce M3 8Go", 4),
        ("Écran Dell UltraSharp U2422H 24\"", "Dell", "U2422H", "Écran IPS Full HD 24 pouces", 15),
        ("Imprimante HP LaserJet Pro M404dn", "HP", "LaserJet Pro M404dn", "Imprimante laser monochrome recto-verso réseau", 5),
        ("Multifonction Epson EcoTank ET-5850", "Epson", "EcoTank ET-5850", "Imprimante multifonction jet d'encre tank réseau", 3),
        ("Serveur Dell PowerEdge R750", "Dell", "PowerEdge R750", "Serveur rack 2U Xeon Silver", 2),
        ("Switch Cisco Catalyst 2960-X 48p", "Cisco", "Catalyst 2960-X", "Switch manageable 48 ports Gigabit", 3),
        ("Onduleur APC Smart-UPS SMT1500", "APC", "SMT1500IC", "Onduleur 1500VA line-interactive", 6),
        ("Routeur MikroTik hEX RB750Gr3", "MikroTik", "RB750Gr3", "Routeur 5 ports Gigabit", 5),
    ],
    "Nettoyage": [
        ("Autolaveuse Karcher BD 50/50 C", "Karcher", "BD 50/50 C Bp Pack", "Autolaveuse électrique 50 cm", 2),
        ("Aspirateur industriel Karcher NT 65/2", "Karcher", "NT 65/2 Ap Me Tee", "Aspirateur eau et poussière 65 L double moteur", 4),
        ("Nettoyeur haute pression Karcher HD 6/15", "Karcher", "HD 6/15-4", "Nettoyeur eau froide 150 bars", 3),
        ("Monobrosse Fimap MS17", "Fimap", "MS 17", "Monobrosse 17 pouces multi-usages", 2),
        ("Chariot de ménage Vileda UltraSpeed", "Vileda", "UltraSpeed Safety", "Chariot lavage complet double seau", 8),
        ("Déshumidificateur Trotec TTK 170", "Trotec", "TTK 170 ECO", "Déshumidificateur 60 L/jour", 3),
        ("Balayeuse mécanique Haaga 477", "Haaga", "477", "Balayeuse manuelle triple brosse 77 cm", 2),
        ("Pulvérisateur Karcher PS 40", "Karcher", "PS 40", "Pulvérisateur à pression désinfection 40 L", 4),
    ],
    "Immobilier": [
        ("Climatiseur split LG Dual Inverter 12000 BTU", "LG", "S4-Q12KL3SE", "Climatiseur mural inverter A++", 6),
        ("Groupe électrogène Honda EC5000 CLR", "Honda", "EC5000 CLR", "Groupe essence 4500 W AVR", 2),
        ("Extincteur CO2 5 kg", "Safex", "CO2-5KG", "Extincteur dioxyde de carbone 5 kg", 12),
        ("Échelle télescopique Centaure 3,80 m", "Centaure", "Telesteps 380", "Échelle télescopique aluminium 3,80 m", 5),
        ("Perceuse à percussion Bosch GSB 18V-55", "Bosch", "GSB 18V-55 Professional", "Perceuse-visseuse à percussion 18V", 7),
        ("Meuleuse d'angle Makita GA4530R", "Makita", "GA4530R", "Meuleuse 115 mm 720 W", 5),
        ("Projecteur LED chantier Bosch GLI VariLED", "Bosch", "GLI VariLED", "Projecteur LED variable 3000 lumens", 8),
        ("Brasseur d'air Master DF20", "Master Climate", "DF20 P", "Ventilateur industriel haute performance", 4),
        ("Scie circulaire Bosch GKS 190", "Bosch", "GKS 190 Professional", "Scie circulaire 1400 mm lame 190 mm", 4),
    ],
}


async def seed_superadmin() -> None:
    async with AsyncSessionLocal() as db:
        existing = await crud_user.get_by_email(
            db, settings.FIRST_SUPERUSER_EMAIL
        )
        if existing:
            print(f"Super admin deja present : {existing.email}")
            return

        user = User(
            email=settings.FIRST_SUPERUSER_EMAIL.lower(),
            username=settings.FIRST_SUPERUSER_USERNAME,
            hashed_password=hash_password(settings.FIRST_SUPERUSER_PASSWORD),
            role=UserRole.SUPERADMIN,
            is_active=True,
        )
        db.add(user)
        await db.commit()
        print(f"Super admin cree : {user.email}")


async def seed_categories() -> None:
    async with AsyncSessionLocal() as db:
        for item in DEFAULT_CATEGORIES:
            existing = await crud_category.get_by_nom(db, item["nom"])
            if existing:
                continue
            await crud_category.create(
                db,
                CategoryCreate(
                    nom=item["nom"], description=item["description"]
                ),
            )
            print(f"Categorie creee : {item['nom']}")


async def seed_statuts() -> None:
    async with AsyncSessionLocal() as db:
        for item in DEFAULT_STATUTS:
            existing = await crud_statut.get_by_nom(db, item["nom"])
            if existing:
                continue
            await crud_statut.create(db, item["nom"], item["description"])
            print(f"Statut cree : {item['nom']}")


async def seed_emplacements() -> None:
    async with AsyncSessionLocal() as db:
        for item in DEFAULT_EMPLACEMENTS:
            existing = await crud_emplacement.get_by_nom(db, item["nom"])
            if existing:
                continue
            await crud_emplacement.create(db, item["nom"])
            print(f"Emplacement cree : {item['nom']}")


async def seed_equipements() -> None:
    """Peuple le stock avec le catalogue par defaut (si base vide)."""
    from app.crud import equipement as crud_equipement
    from app.models.equipement import EtatMateriel
    from app.schemas.equipement import EquipementCreate

    async with AsyncSessionLocal() as db:
        existants = await crud_equipement.list_equipements(db)
        if existants[0]:
            return
        statuts = {s.nom: s.id for s in await crud_statut.list_statuts(db)}
        categories = {
            c.nom: c.id for c in await crud_category.list_categories(db)
        }
        emplacements = await crud_emplacement.list_emplacements(db)
        emplacement_id = emplacements[0].id if emplacements else None
        en_stock = statuts.get("En stock") or next(iter(statuts.values()))

        prefixes = {"Informatique": "INF", "Nettoyage": "NET", "Immobilier": "IMMO"}
        for nom_cat, items in DEFAULT_CATALOGUE.items():
            categorie_id = categories.get(nom_cat)
            if categorie_id is None:
                continue
            prefix = prefixes[nom_cat]
            for i, (nom, marque, modele, description, quantite) in enumerate(items, 1):
                await crud_equipement.create(
                    db,
                    EquipementCreate(
                        reference=f"{prefix}-{i:03d}",
                        nom=nom,
                        marque=marque,
                        modele=modele,
                        description=description,
                        quantite=quantite,
                        categorie_id=categorie_id,
                        statut_id=en_stock,
                        emplacement_id=emplacement_id,
                        etat=EtatMateriel.NEUF,
                    ),
                )
        print("Catalogue materiel initial cree.")


async def run_seed() -> None:
    await seed_superadmin()
    await seed_categories()
    await seed_statuts()
    await seed_emplacements()
    await seed_equipements()
    print("Seed termine.")