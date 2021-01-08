#include <stdio.h>
#include <limits.h>
#include <stdlib.h>
#include <string.h>

struct pair {
    int first;
    double second;
};

typedef struct {
     int sirina;
     int visina;
     char *format;
     int komponenta;
     char *podatci;
} slika;

int main(int argc, char *argv[]){
    
    FILE *slika_file = fopen(argv[1], "rb");
    // printf("%s\n", argv[1]);

    slika *ulaz_slika;
    ulaz_slika = (slika *)malloc(sizeof(slika));

    if (argc != 2){
        perror("Nisu predana 2 argumenta.\n");
        return 1;
    } else if (!slika_file){
        perror("Nije moguce otvoriti sliku.\n");
        return 1;
    }

    /* format slike */
    char format_slike[16];
    fgets(format_slike, sizeof(format_slike), slika_file);
    if (format_slike[0] != 'P' || format_slike[1] != '5'){
        printf("Neispravan format slike 1.\n");
        return 1;
    }
    ulaz_slika->format = format_slike;
    // printf("Format slike: %s", ulaz_slika->format);

    /* velicine slike */
    int m, n;
    if (fscanf(slika_file, "%d %d", &m, &n) != 2) {
		printf("Nepravilna velicina slike.\n");
		return 1;
    }
    ulaz_slika->sirina = m;
    ulaz_slika->visina = n;
    // printf("Sirina slike: %d,\tVisina slike: %d\n", ulaz_slika->sirina, ulaz_slika->visina);
    
    /* komponenta slike */
    int komponenta_slike;
    if (fscanf(slika_file, "%d", &komponenta_slike) != 1) {
		printf("Nemoguce ucitati komponentu slike 1.\n");
		return 1;
	}
    ulaz_slika->komponenta = komponenta_slike;
    // printf("Komponenta slike: %d\n", ulaz_slika->komponenta);

    int lista[16] = {0};
    char broj[2];
    fgets(broj, 2, slika_file);
    while (fgets(broj, 2, slika_file) != NULL) {
        int n = (int)(broj[0]);
        if (n < 0)
            n += ulaz_slika->komponenta;
        lista[n / 16]++;
    }
    // for (int i = 0; i < 16; i++) printf("%d ", lista[i]);
    // printf("\n");

    struct pair pairs[16];
    int broj_blokova = ulaz_slika->sirina * ulaz_slika->visina;
    for (int i = 0; i < 16; i++){
        pairs[i].first = i;
        pairs[i].second = (double)(lista[i]) / broj_blokova;
        printf("%d %f\n", pairs[i].first, pairs[i].second);
    }

    fclose(slika_file);
    return 0;
}