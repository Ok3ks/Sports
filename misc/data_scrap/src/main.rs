fn main() {

    let response = reqwest::blocking::get("https://fantasy.premierleague.com/api/bootstrap-static/");
    let response = response.unwrap().text().unwrap();


    // let document = scraper::Html::parse_document(&response);
    // let lyrics_selector = scraper::Selector::parse("div").unwrap();

    // let selections = document.select(&lyrics_selector).next().unwrap().text().collect::<Vec<_>>();

    for line in selections {
        println!("{}", line);
    }
}
