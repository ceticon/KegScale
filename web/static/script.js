// =================================================
// KEGSCALE WEB
// =================================================


// -------------------------------------------------
// UPPDATERA KEGSCALE-DATA
// -------------------------------------------------

async function updateKegScale() {

    try {

        const response =
            await fetch("/api/weight");

        const data =
            await response.json();


        // Element finns framför allt på index.html

        const status =
            document.getElementById("status");

        const beerDisplayName =
            document.getElementById(
                "beer-display-name"
            );

        const weight =
            document.getElementById("weight");

        const liters =
            document.getElementById("liters");

        const percent =
            document.getElementById("percent");

        const levelBar =
            document.getElementById("level-bar");

        const timestamp =
            document.getElementById("timestamp");


        // -----------------------------------------
        // FEL VID LÄSNING
        // -----------------------------------------

        if (data.error) {

            if (status) {
                status.textContent =
                    "Fel vid läsning av KegScale";

                status.className =
                    "status offline";
            }

            return;
        }


        // -----------------------------------------
        // KEGSCALE OFFLINE
        // -----------------------------------------

        if (!data.online) {

            if (status) {
                status.textContent =
                    "KegScale är inte aktiv";

                status.className =
                    "status offline";
            }

            if (weight) {
                weight.textContent = "--";
            }

            if (liters) {
                liters.textContent = "--";
            }

            if (percent) {
                percent.textContent = "--";
            }

            if (levelBar) {
                levelBar.style.width = "0%";
            }

            if (beerDisplayName) {
                beerDisplayName.textContent =
                    data.beer_name || "--";
            }

            if (timestamp) {
                timestamp.textContent =
                    "Senaste data: "
                    + data.timestamp;
            }

            return;
        }


        // -----------------------------------------
        // KEGSCALE ONLINE
        // -----------------------------------------

        if (status) {

            status.textContent =
                "KegScale online";

            status.className =
                "status online";
        }


        // Ölets namn

        if (beerDisplayName) {

            beerDisplayName.textContent =
                data.beer_name || "--";
        }


        // Total vikt

        if (weight) {

            weight.textContent =
                Number(
                    data.weight_kg
                ).toFixed(2);
        }


        // Liter öl

        if (liters) {

            liters.textContent =
                Number(
                    data.beer_liters
                ).toFixed(1);
        }


        // Fyllnadsgrad

        if (percent) {

            percent.textContent =
                Number(
                    data.fill_percent
                ).toFixed(1);
        }


        // Nivåindikator

        if (levelBar) {

            let level =
                Number(
                    data.fill_percent
                );

            if (level < 0) {
                level = 0;
            }

            if (level > 100) {
                level = 100;
            }

            levelBar.style.width =
                level + "%";
        }


        // Tidstämpel

        if (timestamp) {

            timestamp.textContent =
                "Senast uppdaterad: "
                + data.timestamp;
        }

    }

    catch (error) {

        console.error(
            "Fel vid hämtning:",
            error
        );

        const status =
            document.getElementById(
                "status"
            );

        if (status) {

            status.textContent =
                "Ingen kontakt med servern";

            status.className =
                "status offline";
        }
    }
}


// -------------------------------------------------
// LÄS ÖLNAMN
// -------------------------------------------------

async function loadBeerName() {

    const beerNameInput =
        document.getElementById(
            "beer-name"
        );

    // Finns endast på setup.html

    if (!beerNameInput) {
        return;
    }


    try {

        const response =
            await fetch(
                "/api/beer-name"
            );

        const data =
            await response.json();


        if (data.success) {

            beerNameInput.value =
                data.beer_name;
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
        document.getElementById(
            "beer-name"
        );

    const button =
        document.getElementById(
            "beer-name-button"
        );

    const message =
        document.getElementById(
            "beer-name-message"
        );


    if (!input || !button || !message) {
        return;
    }


    const beerName =
        input.value.trim();


    if (beerName === "") {

        message.textContent =
            "Ölnamnet får inte vara tomt.";

        return;
    }


    button.disabled = true;

    message.textContent =
        "Sparar...";


    try {

        const response =
            await fetch(
                "/api/beer-name",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        beer_name:
                            beerName
                    })
                }
            );


        const data =
            await response.json();


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


    setTimeout(
        function () {

            button.disabled = false;

            message.textContent = "";

        },
        3000
    );
}


// -------------------------------------------------
// NOLLSTÄLL VÅGEN
// -------------------------------------------------

async function tareScale() {

    const button =
        document.getElementById(
            "tare-button"
        );

    const message =
        document.getElementById(
            "tare-message"
        );


    if (!button || !message) {
        return;
    }


    button.disabled = true;

    message.textContent =
        "Nollställer vågen...";


    try {

        const response =
            await fetch(
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


    setTimeout(
        function () {

            button.disabled = false;

            message.textContent = "";

        },
        3000
    );
}


// =================================================
// SIDAN ÄR LADDAD
// =================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {


        // -----------------------------------------
        // SPARA ÖLNAMN
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


        // Enter i ölnamnsfältet

        const beerNameInput =
            document.getElementById(
                "beer-name"
            );

        if (beerNameInput) {

            beerNameInput.addEventListener(
                "keydown",
                function (event) {

                    if (
                        event.key === "Enter"
                    ) {

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
        // START
        // -----------------------------------------

        loadBeerName();

        updateKegScale();


        // Uppdatera vågdata varje sekund

        setInterval(
            updateKegScale,
            1000
        );

    }
);