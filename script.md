#Leagues of interest 
85647 -- Downtown
1088941 -- Uptown

#terminal linux code to run league report
python3 report.py -g 17 -l 85647
python3 report.py -g 17 -l 1088941

#script to copy output report to template directory of django application

cp 'reports/weekly_report/85647_17.json' 'app/Liveproject/templates'

#terminal code to rename json file to match template structure
mv 'app/Liveproject/templates/85647_17.json' 'app/Liveproject/templates/85647.json'
