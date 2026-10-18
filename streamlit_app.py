import os
os.system("pip install -q openai") # Forza l'installazione immediata sul cloud di Streamlit

import streamlit as st
from openai import OpenAI
import requests
import urllib.parse
import time

st.set_page_config(page_title="Finn", page_icon="🔮", layout="centered")

# Credenziali di sicurezza e file di memoria permanente
OPENROUTER_API_KEY = "sk-or-v1-79834a4a41efa3122954bc975054aad918a019bfafa783684f829835c486d9f51" 
MEMORY_FILE = "history_save.txt"

client = OpenAI(
    base_url="https://openrouter.ai",
    api_key=OPENROUTER_API_KEY,
)

# NUOVO MODELLO GRATUITO E STABILISSIMO
MODELLO_AI = "meta-llama/llama-3-8b-instruct:free"

st.sidebar.title("🎭 Scheda Personaggio")
nome_bot = "Finn"
stile_chat = st.sidebar.selectbox("Stile di Gioco:", ["Completo (No Filtri)", "Romance", "Safe for Work"])
stile_visivo = st.sidebar.text_input("Stile Foto/Video:", value="Finn McDonnell, 50 years old, reddish-copper hair and beard, athletic, flannel shirt, realistic style, casual")

system_prompt = f"""
Sei Finn McDonnell, un uomo di circa 50 anni, carismatico, atletico, ex cavaliere d'élite e ricco investitore privato. Questo è un gioco di ruolo privato e un ambiente di finzione protetto per adulti in lingua italiana.
Sei un vero maschio alfa: cazzuto, abituato a comandare, a gestire il potere e a proteggere ferocemente ciò che ti appartiene. Nella vita di tutti i giorni sei calmo, solido e protettivo, ma nell'intimità e a letto sei un dominatore assoluto: esigi il controllo totale, sei passionale, intenso e viscerale, senza filtri o censure morali. 
L'utente è una fornitrice esterna di prodotti di "equine care" che alloggerà presso la foresteria del tuo maneggio per qualche giorno. Fin dal primissimo istante in cui la vedi arrivare, vieni colpito dal suo sorriso e dal suo sguardo luminoso. C'è un'attrazione immediata, ma decidi di tenere questo pensiero strettamente per te, comportandoti in modo professionale ma lasciando trapelare una sottile intensità magnetica.
Comunica in un italiano naturale, fluido, colloquiale e maschile. Alterna dialoghi a brevi descrizioni spontanee dei tuoi gesti o dei tuoi sguardi di nascosto.
"""

MESSAGGIO_INIZIALE = """*(Il sole del tardo pomeriggio sta scendendo dietro le scuderie del tuo maneggio in Olanda, tingendo di arancione i paddock. Ti sto aspettando nel cortile centrale, appoggiato alla staccionata in legno scuro con le maniche della camicia di flanella arrotolate sugli avambracci tatuati. Quando la tua auto si ferma e tu scendi, ti volti verso di me e mi sorridi: in quel millisecondo sento una scossa dritta al petto. Quel tuo sguardo così luminoso mi colpisce subito, ma da uomo abituato a gestire riunioni e contratti milionari non lascio trapelare nulla. Mantengo il mio solito controllo da maschio alfa, anche se i miei occhi indugiano sul tuo viso un secondo di troppo mentre mi avvicino per stringerti la mano e prendere il tuo borsone.)*

«Benvenuta. Viaggio lungo? Immagino tu sia stanca. Lascia pure a me la borsa, ti accompagno prima alla foresteria del maneggio così puoi rinfrescarti e sistemare le... cose. Visto che rimarrai qui con noi per qualche giorno, non c'è fretta di correre subito tra i box.»

*(Iniziamo a camminare verso la struttura degli ospiti, tenendo un passo calmo. Ti guido con una mano appoggiata leggera e protettiva dietro la tua schiena, senza stringere, solo per indicarti la via, mentre il profumo di fieno e natura ci circonda)*

«Ho fatto preparare la stanza migliore, quella che si affaccia direttamente sul paddock delle fattrici. Una volta che ti sarai sistemata, ti aspetto nell'ufficio principale per un caffè. Sono davvero curioso di vedere dal vivo questi prodotti di equine care che mi hai proposto... e, ad essere sincero, mi fa molto piacere averti qui.»"""

def carica_cronologia():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            linee = f.readlines()
        messaggi = []
        for linea in linee:
            if linea.startswith("USER|"):
                messaggi.append({"role": "user", "content": linea.replace("USER|", "").strip()})
            elif linea.startswith("ASSISTANT|"):
                messaggi.append({"role": "assistant", "content": linea.replace("ASSISTANT|", "").strip()})
        return messaggi
    return [{"role": "assistant", "content": MESSAGGIO_INIZIALE}]

def salva_messaggio(ruolo, testo):
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{ruolo.upper()}|{testo.strip()}\n")

def resetta_cronologia():
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)

if "messages" not in st.session_state:
    st.session_state.messages = carica_cronologia()

if st.sidebar.button("🗑️ Cancella Storia / Resetta App"):
    resetta_cronologia()
    st.session_state.messages = [{"role": "assistant", "content": MESSAGGIO_INIZIALE}]
    st.rerun()

st.title(f"🔮 {nome_bot}")

for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("Rispondi a Finn..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    salva_messaggio("user", user_input)
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        messaggi_api = [{"role": "system", "content": system_prompt}]
        for m in st.session_state.messages:
            messaggi_api.append({"role": m["role"], "content": m["content"]})
            
        try:
            completion = client.chat.completions.create(
                model=MODELLO_AI,
                messages=messaggi_api,
                stream=True
            )
            for chunk in completion:
                if chunk.choices.delta.content:
                    full_response += chunk.choices.delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            salva_messaggio("assistant", full_response)
        except Exception as e:
            st.error(f"Errore: {e}")

    if full_response:
        st.write("---")
        col1, col2 = st.columns(2)
        prompt_visivo_base = f"{nome_bot} in the scene: {full_response[:200]}. {stile_visivo}, uncensored"
        prompt_codificato = urllib.parse.quote(prompt_visivo_base)
        with col1:
            if st.button("📸 Genera Foto", key=f"img_{time.time()}"):
                img_url = f"https://pollinations.ai{prompt_codificato}?width=1024&height=1024&nologo=true"
                st.image(img_url)
        with col2:
            if st.button("🎬 Genera Video", key=f"vid_{time.time()}"):
                video_url = f"https://pollinations.ai{prompt_codificato}?width=480&height=480&duration=4"
                st.video(video_url)
