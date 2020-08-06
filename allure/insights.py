from allure import generate_json, generate_html

if __name__ == "__main__":
    print()
    print('=========================================================')
    print('Generating results json file')
    print('=========================================================')
    generate_json.main()
    print()
    print('=========================================================')
    print('Generating HTML report')
    print('=========================================================')
    generate_html.main()
    print('=========================================================')
