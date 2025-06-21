#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <unistd.h>
#include <sys/stat.h>

#define MAX_PRODUITS 100
#define FICHIER_STOCK "stock.txt"
#define PRIX_MIN 0.01f

typedef struct {
    char id[20];
    char nom[50];
    int quantite;
    float prix;
} Produit;

Produit stock[MAX_PRODUITS];
int nombreProduits = 0;

void verifierFichierStock();
void chargerStock();
void sauvegarderStock();
void ajouterProduit();
void modifierProduit();
void supprimerProduit();
void afficherProduits();
void rechercherProduit();
void afficherMenu();
void viderBuffer();

int main() {
    verifierFichierStock();
    chargerStock();
    
    int choix;
    do {
        afficherMenu();
        printf("\nVotre choix (1-6) : ");
        scanf("%d", &choix);
        viderBuffer();
        
        switch(choix) {
            case 1: ajouterProduit(); break;
            case 2: modifierProduit(); break;
            case 3: supprimerProduit(); break;
            case 4: afficherProduits(); break;
            case 5: rechercherProduit(); break;
            case 6: printf("\nMerci d'avoir utilise le système. Au revoir!\n"); break;
            default: printf("\nChoix invalide. Veuillez réessayer.\n");
        }
    } while(choix != 6);
    
    sauvegarderStock();
    return 0;
}

void verifierFichierStock() {
    struct stat buffer;
    if (stat(FICHIER_STOCK, &buffer) != 0) {
        printf("Creation du fichier stock initial...\n");
        FILE *f = fopen(FICHIER_STOCK, "w");
        if (f) {
            fprintf(f, "# Fichier de stock\n");
            fprintf(f, "# Format: ID| Nom| Quantité| Prix\n");
            fclose(f);
        } else {
            perror("Erreur creation fichier");
        }
    }
}

void chargerStock() {
    FILE *fichier = fopen(FICHIER_STOCK, "r");
    if (!fichier) {
        printf("Erreur: Impossible d'ouvrir %s\n", FICHIER_STOCK);
        return;
    }

    char ligne[256];
    while (fgets(ligne, sizeof(ligne), fichier)) {
        if (ligne[0] == '#' || ligne[0] == '\n') continue;
        
        Produit p = {0};
        if (sscanf(ligne, "%19[^|]|%49[^|]|%d|%f", 
                  p.id, p.nom, &p.quantite, &p.prix) >= 4) {
            stock[nombreProduits++] = p;
        }
    }
    fclose(fichier);
}

void sauvegarderStock() {
    FILE *fichier = fopen(FICHIER_STOCK, "w");
    if (!fichier) {
        perror("Erreur ouverture fichier");
        return;
    }

    fprintf(fichier, "# Fichier de stock\n");
    fprintf(fichier, "# Format: ID| Nom| Quantité| Prix\n");
    
    for(int i = 0; i < nombreProduits; i++) {
        fprintf(fichier, "\n%s| %s| %d| %.2f\n",
               stock[i].id,
               stock[i].nom,
               stock[i].quantite,
               stock[i].prix);
    }
    fclose(fichier);
    printf("Sauvegarde reussie dans %s\n", FICHIER_STOCK);
}

void ajouterProduit() {
    if(nombreProduits >= MAX_PRODUITS) {
        printf("\nLe stock est plein! Impossible d'ajouter.\n");
        return;
    }
    
    Produit nouveau = {0};
    
    printf("\nID du produit : ");
    scanf("%19s", nouveau.id);
    viderBuffer();
    
    for(int i = 0; i < nombreProduits; i++) {
        if(!strcmp(stock[i].id, nouveau.id)) {
            printf("\nUn produit avec cet ID existe deja!\n");
            return;
        }
    }
    
    printf("Nom du produit : ");
    fgets(nouveau.nom, sizeof(nouveau.nom), stdin);
    nouveau.nom[strcspn(nouveau.nom, "\n")] = '\0';
    
    printf("Quantite : ");
    while(scanf("%d", &nouveau.quantite) != 1 || nouveau.quantite < 0) {
        printf("Quantite invalide! Recommencez : ");
        viderBuffer();
    }
    
    printf("Prix unitaire (en FrCFA) : ");
    while(scanf("%f", &nouveau.prix) != 1 || nouveau.prix < PRIX_MIN) {
        printf("Prix invalide! Doit être >= %.2f : ", PRIX_MIN);
        viderBuffer();
    }
    viderBuffer();
    
    stock[nombreProduits++] = nouveau;
    printf("\nProduit ajoute avec succes!\n");
}

void modifierProduit() {
    char id[20] = {0};
    printf("\nID du produit à modifier : ");
    scanf("%19s", id);
    viderBuffer();
    
    for(int i = 0; i < nombreProduits; i++) {
        if(!strcmp(stock[i].id, id)) {
            printf("\nNom actuel : %s\n", stock[i].nom);
            printf("Nouveau nom (0 pour conserver) : ");
            
            char buffer[50];
            fgets(buffer, sizeof(buffer), stdin);
            buffer[strcspn(buffer, "\n")] = '\0';
            
            if(strcmp(buffer, "0") != 0) {
                strcpy(stock[i].nom, buffer);
            }
            
            printf("\nQuantite actuelle : %d\n", stock[i].quantite);
            printf("Nouvelle quantite (0 pour conserver) : ");
            int nouvelleQt;
            if(scanf("%d", &nouvelleQt) == 1 && nouvelleQt != 0) {
                stock[i].quantite = nouvelleQt;
            }
            viderBuffer();
            
            printf("\nPrix actuel : %.2f FrCFA\n", stock[i].prix);
            printf("Nouveau prix (0 pour conserver) : ");
            float nouveauPrix;
            if(scanf("%f", &nouveauPrix) == 1 && nouveauPrix != 0) {
                stock[i].prix = nouveauPrix;
            }
            viderBuffer();
            
            printf("\nProduit modifie avec succes!\n");
            return;
        }
    }
    printf("\nProduit non trouve!\n");
}

void supprimerProduit() {
    char id[20] = {0};
    printf("\nID du produit a supprimer : ");
    scanf("%19s", id);
    viderBuffer();
    
    for(int i = 0; i < nombreProduits; i++) {
        if(!strcmp(stock[i].id, id)) {
            for(int j = i; j < nombreProduits - 1; j++) {
                stock[j] = stock[j + 1];
            }
            nombreProduits--;
            printf("\nProduit supprime avec succes!\n");
            return;
        }
    }
    printf("\nProduit non trouve!\n");
}

void afficherProduits() {
    if(!nombreProduits) {
        printf("\nAucun produit en stock.\n");
        return;
    }
    
    float valeurTotale = 0;
    printf("\n%-10s %-30s %-10s %15s %15s\n", 
           "ID", "Nom", "Quantite", "Prix Unitaire", "Valeur Totale");
    printf("---------------------------------------------------------------------------------------\n");
    
    for(int i = 0; i < nombreProduits; i++) {
        float valeur = stock[i].quantite * stock[i].prix;
        printf("%-10s %-30s %-10d %15.2fFrCFA %15.2fFrCFA\n", 
               stock[i].id, 
               stock[i].nom, 
               stock[i].quantite,
               stock[i].prix,
               valeur);
        valeurTotale += valeur;
    }
    
    printf("---------------------------------------------------------------------------------------\n");
    printf("%52s %15.2fFrCFA\n", "Valeur totale du stock:", valeurTotale);
    printf("%52s %15d\n", "Nombre de produits:", nombreProduits);
}

void rechercherProduit() {
    char terme[50] = {0};
    printf("\nTerme de recherche (ID ou nom) : ");
    fgets(terme, sizeof(terme), stdin);
    terme[strcspn(terme, "\n")] = '\0';
    
    int trouve = 0;
    
    printf("\n%-10s %-30s %-10s %15s %15s\n", 
           "ID", "Nom", "Quantite", "Prix Unitaire", "Valeur Totale");
    printf("--------------------------------------------------------------------\n");
    
    for(int i = 0; i < nombreProduits; i++) {
        if(strstr(stock[i].id, terme) || strstr(stock[i].nom, terme)) {
            float valeur = stock[i].quantite * stock[i].prix;
            printf("%-10s %-30s %-10d %15.2fFrCFA %15.2fFrCFA\n", 
                  stock[i].id, 
                  stock[i].nom, 
                  stock[i].quantite,
                  stock[i].prix,
                  valeur);
            trouve = 1;
        }
    }
    
    if(!trouve) {
        printf("Aucun produit trouve pour '%s'\n", terme);
    }
    printf("--------------------------------------------------------------------\n");
}

void afficherMenu() {
    printf("\n========================================");
    printf("\n    SYSTEME DE GESTION DE STOCK");
    printf("\n========================================");
    printf("\n  1. Ajouter un produit");
    printf("\n  2. Modifier un produit");
    printf("\n  3. Supprimer un produit");
    printf("\n  4. Afficher tous les produits");
    printf("\n  5. Rechercher un produit");
    printf("\n  6. Quitter");
    printf("\n========================================");
}

void viderBuffer() {
    int c;
    while((c = getchar()) != '\n' && c != EOF);
}