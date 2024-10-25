use chrono::{Datelike, FixedOffset, NaiveDate, NaiveTime, Utc, Weekday};

const RTDAYS: [Weekday; 3] = [
    Weekday::Wed,
    Weekday::Fri,
    Weekday::Sun,
    ];

const TIME_ZONE :i32 = 3 * 60 * 60; 

pub fn get_next_rt(msg: String) -> (String, i64) {
    let now = Utc::now();
    let mut reply: String = String::from("No date found");
    let today = now.date_naive();
    let mut raiddates = Vec::new();
    let mut raidtimes = Vec::new();
    for i in [0, 7, 14] {
        for day_int in RTDAYS {
            let mut day_offset: i32 = (day_int.num_days_from_monday() as i32) - (today.weekday().num_days_from_monday() as i32);
            day_offset = ((day_offset % 7) + 7) % 7 + i;
            let day = today + chrono::Duration::days(day_offset as i64);
            raiddates.push(day);
        }
    }

    for dates in &raiddates {
        match dates.weekday() {
            Weekday::Wed => raidtimes.push(String::from("21:00")),
            Weekday::Fri => raidtimes.push(String::from("20:00")),
            Weekday::Sun => raidtimes.push(String::from("19:00")),
            _ => raidtimes.push(String::from("00:00")),      
        }
    }

    let mut changes = msg.to_lowercase().replace("переносы:\n", "");
    changes = changes.replace(" -> ", ",");
    changes = changes.replace(" - ", ",");

    let mut reader = csv::ReaderBuilder::new()
        .has_headers(false)
        .flexible(true)
        .from_reader(changes.as_bytes());
    for result in reader.records() {
        let record = result.expect("csv check");
        let change_date = NaiveDate::parse_from_str(&record[0], "%d.%m.%Y");
        let date = change_date.expect("date check");

        let index = raiddates.iter().position(|&i| i == date);
        if index.is_none() {
            if &record[1] != "отмена" {
                raiddates.push(NaiveDate::parse_from_str(&record[1], "%d.%m.%Y").expect("should be date"));
                raidtimes.push(String::from(&record[2]));
            }
            continue;
        }

        let index = index.unwrap();

        if &record[1] == "отмена" {
            raiddates[index] = Default::default();
        } else {
            raiddates[index] =
                NaiveDate::parse_from_str(&record[1], "%d.%m.%Y").expect("should be date");
            if record.len() == 3 {
                raidtimes[index] = String::from(&record[2]);
            }
        }
    }

    let mut zipped: Vec<_> = raiddates.into_iter().zip(raidtimes).collect();
    zipped.sort_unstable();

    let mut ts:i64 = 0;
    for (raid_date, raid_time) in zipped {
        if raid_date == Default::default() || today > raid_date {
            continue;
        } else {
            let time_obj =
                NaiveTime::parse_from_str(&raid_time, "%H:%M").expect("should be time");
            let naive_datetime = raid_date.and_time(time_obj);
            let tz = FixedOffset::east_opt(TIME_ZONE).unwrap();
            let datetime = naive_datetime.and_local_timezone(tz).unwrap();
            ts = datetime.timestamp();
            
            //println!("Now: {} | TS: {} | diff: {}",now.timestamp(), ts, now.timestamp() - ts);
            if now.timestamp() > (ts + 7200)
            {           
                continue;
            }

            let str = format!(
                "Следующий рейд:\n\
                {} - {} (МСК)\n\
                <t:{}:f>",
                
                raid_date.format("%d.%m.%Y"), raid_time,
                ts
            );
            
            reply = String::from(str);
            break;
        }
    }
    return (reply, ts);
}
