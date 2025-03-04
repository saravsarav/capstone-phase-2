function startScan() {
    switchPage('welcomePage', 'scannerPage');
}

function scanWebsite() {
    let url = document.getElementById("url").value;
    if (!url) {
        alert("⚠️ Please enter a valid URL!");
        return;
    }

    switchPage('scannerPage', 'progressPage');

    $.ajax({
        url: "/scan",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ url: url }),
        success: function(response) {
            document.getElementById("resultText").innerText = response.result;
            switchPage('progressPage', 'thankYouPage');
        },
        error: function() {
            document.getElementById("resultText").innerText = "❌ Error scanning the website.";
            switchPage('progressPage', 'thankYouPage');
        }
    });
}

function restart() {
    switchPage('thankYouPage', 'welcomePage');
}

function exitSite() {
    window.close();
}

function switchPage(fromPage, toPage) {
    document.getElementById(fromPage).classList.remove('active');
    setTimeout(() => {
        document.getElementById(fromPage).style.display = 'none';
        document.getElementById(toPage).style.display = 'flex';
        setTimeout(() => {
            document.getElementById(toPage).classList.add('active');
        }, 10);
    }, 500);
}

function toggleTheme() {
    document.body.classList.toggle("dark");
}
