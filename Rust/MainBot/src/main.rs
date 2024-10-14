mod get_rt;

// use chrono::{Datelike, FixedOffset, NaiveDate, NaiveTime, Utc};
use poise::serenity_prelude::{self as serenity}; //, EditMessage};
use regex::Regex;
use crate::get_rt::get_next_rt;

const TOKEN: &str = include_str!(".token");

const CHANNEL_ID: u64 = 989221264143048834;
const PIN_ID: u64 = 991733635575197757;
// const PIN_NEXT_RAID: u64 = 1275458504554971136;

/*
DEBUG
const CHANNEL_ID: u64 = 964233249616453703;
const PIN_ID: u64 = 1275132882003820606;
const PIN_NEXT_RAID: u64 = 1275452265741680691;
*/

// const RTDAYS: [i32; 3] = [0, 2, 5];

type Error = Box<dyn std::error::Error + Send + Sync>;
#[allow(unused)]
type Context<'a> = poise::Context<'a, Data, Error>;

pub struct Data {}

#[tokio::main]
async fn main() {
    env_logger::init();
    let token = TOKEN;
    let intents =
        serenity::GatewayIntents::non_privileged() | serenity::GatewayIntents::MESSAGE_CONTENT;

    let framework = poise::Framework::builder()
        .setup(move |_ctx, _ready, _framework| Box::pin(async move { Ok(Data {}) }))
        .options(poise::FrameworkOptions {
            event_handler: |ctx, event, framework, data| {
                Box::pin(event_handler(ctx, event, framework, data))
            },
            ..Default::default()
        })
        .build();

    let client = serenity::ClientBuilder::new(token, intents)
        .framework(framework)
        .await;

    client.unwrap().start().await.unwrap();
}

async fn event_handler(
    ctx: &serenity::Context,
    event: &serenity::FullEvent,
    _framework: poise::FrameworkContext<'_, Data, Error>,
    _data: &Data,
) -> Result<(), Error> {
    match event {
        serenity::FullEvent::Ready { data_about_bot, .. } => {
            println!("Logged in as {}", data_about_bot.user.name);
        }
        serenity::FullEvent::Message { new_message } => {
            let re = Regex::new(r"к[оа]г?д[аы] (р[еэ]йд|рт)").unwrap();

            if new_message.author.id != ctx.cache.current_user().id
                && new_message.channel_id == CHANNEL_ID
                && re.is_match(&new_message.content.to_lowercase())
            {
                let msguid = serenity::MessageId::new(PIN_ID);
                //let next_raid_pin_id = serenity::MessageId::new(PIN_NEXT_RAID);
                let channel_guid = serenity::ChannelId::new(CHANNEL_ID);
                let reschedule = channel_guid.message(&ctx, msguid).await?;
                let reply: String = get_next_rt(reschedule.content.to_lowercase()).0;
                new_message.reply(ctx, format!("{}", reply)).await?;

                /* 
                let mut old_msg = channel_guid.message(&ctx, next_raid_pin_id).await?;
                if reply != old_msg.content {
                    _ = old_msg
                        .edit(&ctx, EditMessage::new().content(reply))
                        .await?;
                }
                */
            }
        }
        _ => {}
    }
    Ok(())
}