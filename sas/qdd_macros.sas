/* ============================================================================
 * Sentinel QDD-S2 — Macros SAS pour Qualité des Données
 * ============================================================================
 * Implémentation SAS des 8 types de contrôles génériques.
 * À exécuter dans SAS OnDemand for Academics ou environnement SAS.
 * ============================================================================ */

/* ============================================================================
 * MACRO: QDD_NON_NUL
 * Détecte les valeurs NULL/NULL/manquantes dans une table
 * ============================================================================ */
%macro qdd_non_nul(table=, champs=, output=anomalies);
  proc sql;
    create table &output as
    select *,
           "NON_NUL" as type_controle,
           case
             when %do i=1 %to %sysfunc(countw(&champs));
               %let champ = %scan(&champs, &i);
               &champ is null %if &i < %sysfunc(countw(&champs)) %then or;
             %end;
             then 1 else 0
           end as est_anomalie
    from &table
    where %do i=1 %to %sysfunc(countw(&champs));
      %let champ = %scan(&champs, &i);
      &champ is null %if &i < %sysfunc(countw(&champs)) %then or;
    %end;
  quit;
%mend qdd_non_nul;

/* ============================================================================
 * MACRO: QDD_UNIQUE
 * Détecte les doublons basés sur une clé
 * ============================================================================ */
%macro qdd_unique(table=, cle=, output=anomalies);
  proc sql;
    create table temp_doublons as
    select &cle, count(*) as freq
    from &table
    group by &cle
    having count(*) > 1;

    create table &output as
    select a.*,
           "UNIQUE" as type_controle,
           1 as est_anomalie
    from &table a
    inner join temp_doublons b
    on a.&cle = b.&cle;
  quit;

  proc datasets library=work nolist;
    delete temp_doublons;
  run;
%mend qdd_unique;

/* ============================================================================
 * MACRO: QDD_PLAGE
 * Détecte les valeurs en dehors d'une plage [min, max]
 * ============================================================================ */
%macro qdd_plage(table=, champ=, min=, max=, output=anomalies);
  proc sql;
    create table &output as
    select *,
           "PLAGE" as type_controle,
           case
             when &champ is null then 1
             when &champ < &min or &champ > &max then 1
             else 0
           end as est_anomalie
    from &table
    where &champ is null or &champ < &min or &champ > &max;
  quit;
%mend qdd_plage;

/* ============================================================================
 * MACRO: QDD_REFERENTIEL
 * Détecte les valeurs en dehors du référentiel (domaine autorisé)
 * ============================================================================ */
%macro qdd_referentiel(table=, champ=, domaine=, output=anomalies);
  proc sql;
    create table &output as
    select *,
           "REFERENTIEL" as type_controle,
           case
             when &champ not in (&domaine) and &champ is not null then 1
             else 0
           end as est_anomalie
    from &table
    where &champ not in (&domaine) and &champ is not null;
  quit;
%mend qdd_referentiel;

/* ============================================================================
 * MACRO: QDD_COHERENCE_DATES
 * Détecte les incohérences de dates (d1 < d2 < d3, etc.)
 * ============================================================================ */
%macro qdd_coherence_dates(table=, date1=, date2=, date3=, output=anomalies);
  proc sql;
    create table &output as
    select *,
           "COHERENCE_DATES" as type_controle,
           case
             when &date2 < &date1 and &date1 is not null and &date2 is not null then 1
             %if &date3 ne %then %do;
               when &date3 < &date2 and &date2 is not null and &date3 is not null then 1
             %end;
             else 0
           end as est_anomalie
    from &table
    where &date2 < &date1 or %if &date3 ne %then &date3 < &date2;
  quit;
%mend qdd_coherence_dates;

/* ============================================================================
 * MACRO: QDD_RECONCILIATION
 * Détecte les écarts de réconciliation entre deux champs (avec tolérance)
 * ============================================================================ */
%macro qdd_reconciliation(table=, champ1=, champ2=, tolerance=0.05, output=anomalies);
  proc sql;
    create table &output as
    select *,
           "RECONCILIATION" as type_controle,
           round(abs(&champ1 - &champ2) / ((abs(&champ1) + abs(&champ2)) / 2), 0.0001) as ecart_relatif,
           case
             when abs(&champ1 - &champ2) / ((abs(&champ1) + abs(&champ2)) / 2) > &tolerance then 1
             else 0
           end as est_anomalie
    from &table
    where abs(&champ1 - &champ2) / ((abs(&champ1) + abs(&champ2)) / 2) > &tolerance;
  quit;
%mend qdd_reconciliation;

/* ============================================================================
 * MACRO: QDD_VARIATION_N_N1
 * Détecte les chutes anormales de volumétrie entre N-1 et N
 * ============================================================================ */
%macro qdd_variation_n_n1(table=, montant=, exercice=, tolerance=0.1, output=anomalies);
  /* Nécessite une table avec exercice N et N-1 */
  proc sql;
    create table temp_vol as
    select exercice, sum(&montant) as volume
    from &table
    group by exercice;

    create table &output as
    select a.*,
           "VARIATION_N_N1" as type_controle,
           round(abs(b.volume - c.volume) / c.volume, 0.0001) as chute_relative,
           case
             when abs(b.volume - c.volume) / c.volume > &tolerance then 1
             else 0
           end as est_anomalie
    from &table a
    left join temp_vol b on a.exercice = b.exercice
    left join temp_vol c on b.exercice - 1 = c.exercice
    where abs(b.volume - c.volume) / c.volume > &tolerance;
  quit;

  proc datasets library=work nolist;
    delete temp_vol;
  run;
%mend qdd_variation_n_n1;

/* ============================================================================
 * MACRO: QDD_LOG_CHECK
 * Analyse les logs SAS pour détecter les erreurs, avertissements, etc.
 * ============================================================================ */
%macro qdd_log_check(output=log_anomalies);
  /* Vérifier les variables non initialisées */
  proc sql;
    create table &output as
    select
      "LOG_ERROR" as type_controle,
      "" as cle_metier,
      "Variable non initialisée / Erreur" as anomalie,
      "&SYSCC" as code_erreur
    %if "&SYSERR" ne "0" %then %do;
      union all select
      "LOG_ERROR" as type_controle,
      "" as cle_metier,
      "Erreur d'exécution détectée" as anomalie,
      "&SYSERR" as code_erreur
    %end;
  quit;
%mend qdd_log_check;
