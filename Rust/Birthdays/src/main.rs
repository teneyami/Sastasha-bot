use chrono;
use std::collections::HashMap;
use reqwest::header;
const TOKEN: &str = concat!("bot ", include_str!(".token"));
const CHANNEL_ID: u64 = 989221264143048834;
//const CHANNEL_ID: u64 = 964233249616453703;

fn send_congrats(msg: String) -> Result<(), reqwest::Error> {
    let endpoint : String = format!("https://discord.com/api/v10/channels/{CHANNEL_ID}/messages");
    let mut headers = header::HeaderMap::new();
    headers.insert("Authorization", header::HeaderValue::from_static(TOKEN));
    headers.insert("User-Agent", header::HeaderValue::from_static("DiscordBot"));
    let client = reqwest::blocking::Client::builder()
    .default_headers(headers)
    .build()?;

    let mut msg_builder = std::collections::HashMap::new();
    msg_builder.insert("content", msg);
    client.post(&endpoint)
        .json(&msg_builder)
        .send()?;

    Ok(())
}

fn main() {
    let today = chrono::Utc::now().date_naive().format("%d.%m").to_string();
    let birthday_dict = HashMap::from([
        ("Настя", "21.01"),
        ("Паша", "06.08"),
        ("Дима", "25.07"),
        ("Tene", "22.08"),
        ("Morgaza", "06.10"),
        ("Skydes", "26.12"),
        ("Mikoto", "03.09"),
        ("Raikou", "09.06"),
        ("Fenny", "24.08"),
    ]);

    for (name, date) in birthday_dict {
        if today == date {
            println!("found bd {}",name);
            let msg = format!("<@&989220836554711051> {name} с днем рождения!!!");
            loop {
                match send_congrats(msg.clone()) {
                    Ok(()) => break,
                    Err(e) => {
                        println!("failed to send: {}", e);
                        std::thread::sleep(std::time::Duration::from_secs(5));
                        continue;
                    }
                }
            }
        }
    }
}