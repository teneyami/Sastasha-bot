use reqwest::header;
use chrono;

mod get_rt;
use crate::get_rt::get_next_rt;

const TOKEN: &str = concat!("Bot ", include_str!(".token"));
const CHANNEL_ID: u64 = 989221264143048834;
const PIN_ID: u64 = 991733635575197757;
const PIN_NEXT_RAID: u64 = 1275458504554971136;

//const CHANNEL_ID: u64 = 964233249616453703;
//const PIN_ID: u64 = 1275132882003820606;
//const PIN_NEXT_RAID: u64 = 1275452265741680691;


fn invoke_rest() -> Result<(), reqwest::Error> {
    let mut headers = header::HeaderMap::new();
    headers.insert("Authorization", header::HeaderValue::from_static(TOKEN));
    headers.insert("User-Agent", header::HeaderValue::from_static("DiscordBot"));
    let client = reqwest::blocking::Client::builder()
        .default_headers(headers)
        .build()?;

    let endpoint : String = format!("https://discord.com/api/v10/channels/{CHANNEL_ID}/messages");
    let uri: String = format!("{endpoint}/{PIN_ID}");
    let res = client.get(uri).send()?;
    let body = res.text()?;
    let json = json::parse(&body).unwrap();
    let next_rt_tupple = get_next_rt(json["content"].to_string());
    let next_rt = next_rt_tupple.0;
    let _ = next_rt_tupple.1;

    println!("{next_rt}");



    
    Ok(())
}
fn main() {
    loop {
        match invoke_rest() {
            Ok(()) => break,
            Err(e) => {
                println!("failed to send: {}", e);
                std::thread::sleep(std::time::Duration::from_secs(5));
                continue;
            }
        }
    }
}