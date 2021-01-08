#include <stdio.h>
#include <stdlib.h>
#include <malloc.h>
#include <math.h>

#define BLOK 16

typedef struct {
     int sirina;
     int visina;
     char *format;
     int komponenta;
     char *podatci;
} slika;

int main (int argc, char *argv[]){
    int x_blok = atoi(argv[1]);

    FILE *slika1 = fopen("lenna.pgm", "rb");
	FILE *slika2 = fopen("lenna1.pgm", "rb");

    slika *ulaz_slika1;
	slika *ulaz_slika2;

    ulaz_slika1 = (slika *)malloc(sizeof(slika));
    ulaz_slika2 = (slika *)malloc(sizeof(slika));

    /* neispravan broj ulaznih parametara i neispravne slike */
    if (argc != 2){
        printf("Nisu predana 2 argumenta.\n");
        return 1;
    }else if (!slika1){
        printf("Nije moguce otvoriti sliku lenna1.pgm.\n");
        return 1;
    } else if (!slika2){
        printf("Nije moguce otvoriti sliku lenna.pgm.\n");
        return 1;
    }

    /* formati slika */
    char format_slike[16];
    fgets(format_slike, sizeof(format_slike), slika1);
    if (format_slike[0] != 'P' || format_slike[1] != '5'){
        printf("Neispravan format slike 1.\n");
        return 1;
    }
    ulaz_slika1->format = format_slike;
    fgets(format_slike, sizeof(format_slike), slika2);
    if (format_slike[0] != 'P' || format_slike[1] != '5'){
        printf("Neispravan format slike 2.\n");
        return 1;
    }
    ulaz_slika2->format = format_slike;

    /* velicine slika */
    int m, n;
    if (fscanf(slika1, "%d %d", &m, &n) != 2) {
		printf("Nepravilna velicina slike 1.\n");
		return 1;
    }
    ulaz_slika1->sirina = m;
    ulaz_slika1->visina = n;

    if (fscanf(slika2, "%d %d", &m, &n) != 2) {
		printf("Nepravilna velicina slike 2.\n");
		return 1;
    }
    ulaz_slika2->sirina = m;
    ulaz_slika2->visina = n;

    /* komponente slika */
    int komponenta_slike;
    if (fscanf(slika1, "%d", &komponenta_slike) != 1) {
		printf("Nemoguce ucitati komponentu slike 1.\n");
		return 1;
	}
    ulaz_slika1->komponenta = komponenta_slike;
    if (fscanf(slika2, "%d", &komponenta_slike) != 1) {
		printf("Nemoguce ucitati komponentu slike 2.\n");
		return 1;
	}
    ulaz_slika2->komponenta = komponenta_slike;

    ulaz_slika1->podatci = (char *)malloc(ulaz_slika1->sirina * ulaz_slika1->visina *sizeof(char));
	fread(ulaz_slika1->podatci, ulaz_slika1->sirina, ulaz_slika1->visina, slika1);

    ulaz_slika2->podatci = (char *)malloc(ulaz_slika2->sirina * ulaz_slika2->visina *sizeof(char));
	fread(ulaz_slika2->podatci, ulaz_slika2->sirina, ulaz_slika2->visina, slika2);

    int i = 0, j = 0, k = 0, l = 0;

    int red1 = (int)floor(x_blok / (ulaz_slika2->sirina / BLOK));
    int stupac1 = x_blok - red1 * (ulaz_slika2->sirina / BLOK);

    int red = stupac1 * BLOK;
    int stupac = red1 * BLOK;

    int trazeni_blok[BLOK][BLOK] = {0};
    int granica = (x_blok % (2 * BLOK)) * BLOK + (x_blok / (2 * BLOK)) * BLOK * ulaz_slika2->sirina;
    for (i = 0; i < BLOK; i++){
        for (j = granica, k = 0; j < granica + BLOK; j++, k++){
                trazeni_blok[i][k] = ulaz_slika2->podatci[j + 1];
                // printf("%d ", trazeni_blok[i][k]);
            }
        // printf("\n");
        granica += ulaz_slika2->sirina;
    }

    int x_pocetak, x_kraj, y_pocetak, y_kraj;
    x_pocetak = (red - BLOK < 0) ? 0 : red - BLOK;
    x_kraj = ((red + (2 * BLOK)) > ulaz_slika2->sirina) ? ulaz_slika2->sirina - BLOK : red + BLOK;
    y_pocetak = (stupac - BLOK < 0) ? 0 : stupac - BLOK;
    y_kraj = ((stupac + (2 * BLOK)) > ulaz_slika2->visina) ? ulaz_slika2->visina - BLOK : stupac + BLOK;
    // printf("%d %d\n", x_pocetak, x_kraj);
    // printf("%d %d\n", y_pocetak, y_kraj);
    
    double mad = 0.0;
    double min_mad = INFINITY;
    int x_vektor, y_vektor;

    for (i = y_pocetak; i <= y_kraj; i++){
        for (j = x_pocetak; j <= x_kraj; j++){
            for (k = 0; k < 16; k++){
                for (l = 0; l < 16; l++){
                        mad += abs(trazeni_blok[k][l] - (ulaz_slika1->podatci[(i + k) * ulaz_slika1->sirina + (j + 1 + l)]));
                }
            }
            // printf("%f\n", mad);
            mad = mad / (BLOK * BLOK);
            if (mad < min_mad){
                min_mad = mad;
                x_vektor = j - red;
                y_vektor = i - stupac;
                // printf("(%d,%d), MAD: %f\n", vektor_x, vektor_y, min_mad);
            }
            mad = 0;
        }
    }
    printf("%d,%d\n", x_vektor, y_vektor);

}
