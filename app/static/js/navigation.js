// Fonction pour gérer la navigation
function navigateTo(url) {
    console.log("Navigation vers:", url);
    window.location.href = url;
}

// Gestionnaires d'événements pour la navigation
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM chargé, initialisation de la navigation");
    
    // Gestionnaire pour le bouton d'inscription
    const registerBtn = document.getElementById('registerBtn');
    console.log("Bouton d'inscription trouvé:", registerBtn);
    if (registerBtn) {
        registerBtn.addEventListener('click', function(e) {
            console.log("Clic sur le bouton d'inscription");
            e.preventDefault();
            navigateTo('/auth/register');
        });
    }

    // Gestionnaire pour le bouton de connexion
    const loginBtn = document.getElementById('loginBtn');
    console.log("Bouton de connexion trouvé:", loginBtn);
    if (loginBtn) {
        loginBtn.addEventListener('click', function(e) {
            console.log("Clic sur le bouton de connexion");
            e.preventDefault();
            navigateTo('/auth/login');
        });
    }

    // Gestionnaire pour le bouton de déconnexion
    const logoutBtn = document.getElementById('logoutBtn');
    console.log("Bouton de déconnexion trouvé:", logoutBtn);
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            console.log("Clic sur le bouton de déconnexion");
            e.preventDefault();
            navigateTo('/auth/logout');
        });
    }

    // Gestionnaire pour le bouton du tableau de bord
    const dashboardBtn = document.getElementById('dashboardBtn');
    console.log("Bouton du tableau de bord trouvé:", dashboardBtn);
    if (dashboardBtn) {
        dashboardBtn.addEventListener('click', function(e) {
            console.log("Clic sur le bouton du tableau de bord");
            e.preventDefault();
            navigateTo('/dashboard');
        });
    }
});
