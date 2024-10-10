from ehrql import codelist_from_csv

# Import pharmacy first conditions codelist
pharmacy_first_conditions_codelist = codelist_from_csv(
    "codelists/user-chriswood-pharmacy-first-clinical-pathway-conditions.csv",
    column="code",
    category_column="term",
)

# Import ethnicity codelist
ethnicity_codelist = codelist_from_csv(
    "codelists/opensafely-ethnicity-snomed-0removed.csv",
    column="snomedcode",
    category_column="Grouping_6",
)

# Import pregnancy codelist
pregnancy_codelist = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-preg_cod.csv",
    column="code",
    category_column="term",
)