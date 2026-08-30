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
// HÄMTA ÖLNAMN
// -------------------------------------------------

async function loadBeerName() {
    try {
        const response = await fetch("/api/beer-name");
        const data = await response.json();

        const beerNameInput =
            document.getElementById("beer-name");

        if (!beerNameInput) {
            return;
        }

        if (data.success) {
            beerNameInput.value = data.beer_name;
        }
        else {
            console.error(
                "Kunde inte läsa ölnamn:",
                data.error
            );
        }
    }

    catch (error) {
        console.error(
            "Fel vid hämtning av ölnamn:",
            error
        );
    }
}


// -------------------------------------------------
// SPARA ÖLNAMN
// -------------------------------------------------

async function saveBeerName() {
    const input =
        document.getElementById("beer-name");

    const button =
        document.getElementById("beer-name-button");

    const message =
        document.getElementById("beer-name-message");

    const beerName = input.value.trim();

    if (beerName === "") {
        message.textContent =
            "Ölnamnet får inte vara tomt.";
        return;
    }

    button.disabled = true;
    message.textContent = "Sparar...";

    try {
        const response = await fetch(
            "/api/beer-name",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    beer_name: beerName
                })
            }
        );

        const data = await response.json();

        if (data.success) {
            message.textContent =
                "Ölnamnet sparades.";
        }
        else {
            message.textContent =
                "Kunde inte spara ölnamnet.";
        }
    }

    catch (error) {
        console.error(
            "Fel vid sparning av ölnamn:",
            error
        );

        message.textContent =
            "Ingen kontakt med servern.";
    }

    setTimeout(function () {
        button.disabled = false;
        message.textContent = "";
    }, 3000);
}


// -------------------------------------------------
// NOLLSTÄLL VÅGEN
// -------------------------------------------------

async function tareScale() {
    const button =
        document.getElementById("tare-button");

    const message =
        document.getElementById("tare-message");

    button.disabled = true;
    message.textContent =
        "Nollställer vågen...";

    try {
        const response = await fetch(
            "/api/tare",
            {
                method: "POST"
            }
        );

        const data =
            await response.json();

        if (data.success) {
            message.textContent =
                "Tarering begärd...";
        }
        else {
            message.textContent =
                "Tareringen misslyckades.";
        }
    }

    catch (error) {
        console.error(
            "Fel vid tarering:",
            error
        );

        message.textContent =
            "Ingen kontakt med servern.";
    }

    setTimeout(function () {
        button.disabled = false;
        message.textContent = "";
    }, 3000);
}


// -------------------------------------------------
// START NÄR SIDAN ÄR FÄRDIGLADDAD
// -------------------------------------------------

document.addEventListener(
    "DOMContentLoaded",
    function () {

        // -----------------------------------------
        // ÖLNAMN
        // -----------------------------------------

        const beerNameButton =
            document.getElementById(
                "beer-name-button"
            );

        if (beerNameButton) {
            beerNameButton.addEventListener(
                "click",
                saveBeerName
            );
        }


        // Spara även med Enter
        const beerNameInput =
            document.getElementById(
                "beer-name"
            );

        if (beerNameInput) {
            beerNameInput.addEventListener(
                "keydown",
                function (event) {

                    if (event.key === "Enter") {
                        saveBeerName();
                    }
                }
            );
        }


        // -----------------------------------------
        // TARERING
        // -----------------------------------------

        const tareButton =
            document.getElementById(
                "tare-button"
            );

        if (tareButton) {
            tareButton.addEventListener(
                "click",
                tareScale
            );
        }


        // -----------------------------------------
        // STARTA DATAUPPDATERING
        // -----------------------------------------

        loadBeerName();

        updateKegScale();

        setInterval(
            updateKegScale,
            1000
        );
    }
);