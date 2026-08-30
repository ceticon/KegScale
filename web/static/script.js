// -------------------------------------------------
// KEG-SCALE WEB
// -------------------------------------------------


// -------------------------------------------------
// HÄMTA OCH VISA DATA
// -------------------------------------------------

async function updateKegScale() {
    try {
        const response = await fetch("/api/weight");
        const data = await response.json();

        const status = document.getElementById("status");
        const weight = document.getElementById("weight");
        const liters = document.getElementById("liters");
        const percent = document.getElementById("percent");
        const levelBar = document.getElementById("level-bar");
        const timestamp = document.getElementById("timestamp");

        // Fel från Flask
        if (data.error) {
            status.textContent = "Fel vid läsning av Keg-Scale";
            status.className = "status offline";
            return;
        }

        // Keg-Scale är inte aktiv
        if (!data.online) {
            status.textContent = "Keg-Scale är inte aktiv";
            status.className = "status offline";

            weight.textContent = "--";
            liters.textContent = "--";
            percent.textContent = "--";

            levelBar.style.width = "0%";

            timestamp.textContent =
                "Senaste data: " + data.timestamp;

            return;
        }

        // Keg-Scale är online
        status.textContent = "Keg-Scale online";
        status.className = "status online";

        // Visa värden
        weight.textContent =
            Number(data.weight_kg).toFixed(2);

        liters.textContent =
            Number(data.beer_liters).toFixed(1);

        percent.textContent =
            Number(data.fill_percent).toFixed(1);

        // Nivåindikator
        let level = Number(data.fill_percent);

        if (level < 0) {
            level = 0;
        }

        if (level > 100) {
            level = 100;
        }

        levelBar.style.width = level + "%";

        // Tidstämpel
        timestamp.textContent =
            "Senast uppdaterad: " + data.timestamp;
    }

    catch (error) {
        console.error("Fel vid hämtning:", error);

        const status = document.getElementById("status");

        if (status) {
            status.textContent = "Ingen kontakt med servern";
            status.className = "status offline";
        }
    }
}


// -------------------------------------------------
// NOLLSTÄLL VÅGEN
// -------------------------------------------------

async function tareScale() {
    const button = document.getElementById("tare-button");
    const message = document.getElementById("tare-message");

    button.disabled = true;
    message.textContent = "Nollställer vågen...";

    try {
        const response = await fetch("/api/tare", {
            method: "POST"
        });

        const data = await response.json();

        if (data.success) {
            message.textContent = "Tarering begärd...";
        }
        else {
            message.textContent = "Tareringen misslyckades.";
        }
    }

    catch (error) {
        console.error("Fel vid tarering:", error);

        message.textContent =
            "Ingen kontakt med servern.";
    }

    // Aktivera knappen igen efter 3 sekunder
    setTimeout(function () {
        button.disabled = false;
        message.textContent = "";
    }, 3000);
}


// -------------------------------------------------
// START NÄR HTML-SIDAN ÄR FÄRDIGLADDAD
// -------------------------------------------------

document.addEventListener("DOMContentLoaded", function () {

    // Koppla Nollställ-knappen
    const tareButton =
        document.getElementById("tare-button");

    if (tareButton) {
        tareButton.addEventListener(
            "click",
            tareScale
        );
    }

    // Läs vikt direkt
    updateKegScale();

    // Uppdatera därefter varje sekund
    setInterval(
        updateKegScale,
        1000
    );
});