import streamlit as st
import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

st.set_page_config(page_title="IA Email Sender", page_icon="📧")
st.title("📧 IA Email Sender - Envoie à 1 ou 1000 personnes")

# SIDEBAR POUR CONFIG SMTP
st.sidebar.header("1. Configuration SMTP")
st.sidebar.info("Utilise Gmail, Outlook, ou ton propre serveur SMTP")

smtp_server = st.sidebar.selectbox("Serveur SMTP", ["smtp.gmail.com", "smtp.office365.com", "smtp.mail.yahoo.com"])
smtp_port = st.sidebar.number_input("Port", 587)
email_sender = st.sidebar.text_input("Ton Email")
password = st.sidebar.text_input("Mot de passe / App Password", type="password")

st.sidebar.warning("Pour Gmail: active 'Mot de passe d'application' dans Google Account > Sécurité")

# ONGLES : 1 A 1 OU EN MASSE
tab1, tab2 = st.tabs(["✉️ Envoi Simple", "📊 Envoi en Masse CSV"])

with tab1:
    st.header("Envoyer à 1 personne")
    email_receiver = st.text_input("Email du destinataire")
    subject = st.text_input("Objet du mail")
    body = st.text_area("Message", height=200)
    
    if st.button("Envoyer le Mail"):
        if not all([email_sender, password, email_receiver, subject, body]):
            st.error("Remplis tous les champs")
        else:
            try:
                msg = MIMEMultipart()
                msg['From'] = email_sender
                msg['To'] = email_receiver
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'html'))

                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(email_sender, password)
                server.sendmail(email_sender, email_receiver, msg.as_string())
                server.quit()
                st.success(f"✅ Mail envoyé à {email_receiver}")
            except Exception as e:
                st.error(f"Erreur: {e}")

with tab2:
    st.header("Envoyer à plusieurs personnes via CSV")
    st.write("Upload un CSV avec colonnes: `email`, `nom`, `entreprise`")
    st.code("email,nom,entreprise\njohn@gmail.com,John,Google")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    subject_mass = st.text_input("Objet pour tout le monde")
    body_template = st.text_area("Template de mail. Utilise {nom} et {entreprise}", 
                                 "Bonjour {nom},\n\nJe vous contacte de la part de {entreprise}...")
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df)

        if st.button("Lancer Campagne d'Emails"):
            if not all([email_sender, password, subject_mass, body_template]):
                st.error("Remplis tous les champs")
            else:
                progress = st.progress(0)
                status = st.empty()
                success_count = 0

                try:
                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    server.login(email_sender, password)

                    for i, row in df.iterrows():
                        # PERSONNALISATION
                        body_personnalise = body_template.format(nom=row['nom'], entreprise=row['entreprise'])
                        
                        msg = MIMEMultipart()
                        msg['From'] = email_sender
                        msg['To'] = row['email']
                        msg['Subject'] = subject_mass
                        msg.attach(MIMEText(body_personnalise, 'html'))

                        server.sendmail(email_sender, row['email'], msg.as_string())
                        success_count += 1
                        status.text(f"Envoyé à {row['email']}")
                        progress.progress((i+1)/len(df))
                        time.sleep(1) # Pour ne pas être blacklisté par Gmail

                    server.quit()
                    st.success(f"✅ Campagne terminée! {success_count}/{len(df)} emails envoyés")

                except Exception as e:
                    st.error(f"Erreur: {e}")
