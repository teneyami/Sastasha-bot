use chrono::{Datelike, FixedOffset, NaiveDate, NaiveTime, Utc};
const RTDAYS: [i32; 3] = [0, 2, 5];

pub fn get_next_rt(msg: String) -> (String, i64) {
    let now = Utc::now();
    let mut reply: String = String::from("No date found");
    let today = now.date_naive();
    let mut raiddates: [NaiveDate; 9] = [Default::default(); 9];
    let mut raidtimes: [String; 9] = Default::default();
    let mut index = 0;
    let mut ts: i64 =0;
    for i in [0, 7, 14] {
        for day_int in RTDAYS {
            let mut day_offset: i32 = day_int - (today.weekday().num_days_from_monday() as i32);
            day_offset = ((day_offset % 7) + 7) % 7 + i;
            let day = today + chrono::Duration::days(day_offset as i64);
            raiddates[index] = day;
            index += 1;
        }
    }

    raiddates.sort();
    for i in 0..raiddates.len() {
        let week_day = raiddates[i].weekday().num_days_from_monday();
        if week_day == 5 {
            raidtimes[i] = String::from("19:00");
        } else {
            raidtimes[i] = String::from("20:00");
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

    for i in 0..raiddates.len() {
        if raiddates[i] == Default::default() {
            continue;
        } else {
            let formated_date = format!("{} - {}", raiddates[i].format("%d.%m.%Y"), raidtimes[i]);
            let time_obj =
                NaiveTime::parse_from_str(&raidtimes[i], "%H:%M").expect("should be time");
            let naive_datetime = raiddates[i].and_time(time_obj);
            let tz = FixedOffset::east_opt(10800).unwrap();
            let datetime = naive_datetime.and_local_timezone(tz).unwrap();

            let str = format!(
                "Следующий рейд:\n\
            {} (МСК)\n\
            <t:{}:f>",
                formated_date,
                datetime.timestamp()
            );
            ts = datetime.timestamp();
            reply = String::from(str);
            break;
        }
    }
    return (reply, ts);
}
