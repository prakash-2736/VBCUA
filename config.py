import os

# General UI settings
APP_TITLE = "Voice-Based Concept Understanding Analyser (VBCUA)"
APP_ICON = "🎙️"

# Path settings
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

REFERENCE_CONCEPTS = {
    "Object-Oriented Programming (OOP)": (
        "Object-Oriented Programming is a programming paradigm based on the concept of 'objects', "
        "which can contain data in the form of fields (attributes or properties) and code in the form of "
        "procedures (methods). The four core principles of OOP are encapsulation, which hides internal details "
        "and exposes a public interface; inheritance, which allows a class to inherit features from another; "
        "polymorphism, which allows different classes to respond to the same message in unique ways; "
        "and abstraction, which simplifies complex systems by modeling classes based on their essential characteristics."
    ),
    "TCP/IP Three-Way Handshake": (
        "The TCP three-way handshake is the process used in a TCP/IP network to make a connection between a client "
        "and a server. It consists of three steps. First, the client sends a SYN (synchronize) packet to the server "
        "to initiate the connection. Second, the server responds with a SYN-ACK (synchronize-acknowledge) packet to "
        "acknowledge the client's request and express willingness to connect. Third, the client sends an ACK "
        "(acknowledge) packet back to the server to confirm receipt. After these three steps, a reliable connection "
        "is established, and data transmission can begin."
    ),
    "Photosynthesis": (
        "Photosynthesis is the process used by plants, algae, and certain bacteria to harness energy from sunlight "
        "and turn it into chemical energy. The general chemical equation is carbon dioxide plus water in the presence "
        "of light and chlorophyll yields glucose and oxygen. It occurs in two main stages: the light-dependent reactions, "
        "which take place in the thylakoid membranes of chloroplasts and capture solar energy to produce ATP and NADPH; "
        "and the light-independent reactions (or Calvin Cycle), which occur in the stroma and use that ATP and NADPH "
        "to fix carbon dioxide into sugars like glucose."
    ),
    "Database Normalization": (
        "Database normalization is the process of structuring a relational database in accordance with a series of "
        "normal forms in order to reduce data redundancy and improve data integrity. The first three normal forms are: "
        "First Normal Form (1NF), which requires that table cells contain atomic values and there are no repeating groups; "
        "Second Normal Form (2NF), which requires that the table is in 1NF and all non-key attributes are fully dependent "
        "on the entire primary key; and Third Normal Form (3NF), which requires that the table is in 2NF and there are "
        "no transitive dependencies, meaning non-key fields must depend only on the primary key, and not on other non-key fields."
    )
}
