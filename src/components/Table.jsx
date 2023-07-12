import axios from "axios";
import { Stack } from "@mantine/core";
import TableEntry from "./TableEntry";


export default function Table() {

  // let items = axios.get();
  // Temporary items for testing...
  const temp = [
    {"url": "https://www.tripadvisor.com/Restaurant_Review-g1066444-d3778588-Reviews-Tendon_Kaneko_Hannosuke_Nihombashi_Honten-Chuo_Tokyo_Tokyo_Prefecture_Kanto.html", "imgs": ["https://media-cdn.tripadvisor.com/media/photo-f/19/9c/49/d1/caption.jpg", "https://media-cdn.tripadvisor.com/media/photo-s/11/9b/e3/10/950.jpg"], "name": "Tendon Kaneko Hannosuke NihoTendon Kaneko Hannosuke NihoTendon Kaneko Hannosuke NihoTendon Kaneko Hannosuke Nihombashi Honten", "address": "1-11-15 Nihombashi Muromachi, Chuo 103-0022 Tokyo Prefecture", "phone": "+81 3-3243-0707", "id": "4301548453822875", "rating": 4, "review_count": 359, "tags": ["Mid-range", "Japanese"], "price": "$$ - $$$"},
    {"url": "https://www.tripadvisor.com/Restaurant_Review-g14133673-d3816764-Reviews-Coco_Ichibanya_Shinjuku_Station_West_Entrance-Nishishinjuku_Shinjuku_Tokyo_Toky.html", "imgs": ["https://media-cdn.tripadvisor.com/media/photo-s/13/80/ff/78/photo0jpg.jpg", "https://media-cdn.tripadvisor.com/media/photo-f/0a/8c/72/9e/caption.jpg"], "name": "Coco Ichibanya Shinjuku Station West Entrance", "address": "1-2-12, Nishishinjuku, Shinjuku 160-0023 Tokyo Prefecture", "phone": "+81 3-3345-0775", "id": "9268528026785253", "rating": 4, "review_count": 366, "tags": ["Cheap Eats", "Japanese", "Vegetarian Friendly", "Vegan Options"], "price": "$"},
    {"url": "https://www.tripadvisor.com/Restaurant_Review-g14129735-d1688108-Reviews-Atelier_Morimoto_Xex-Roppongi_Minato_Tokyo_Tokyo_Prefecture_Kanto.html", "imgs": ["https://media-cdn.tripadvisor.com/media/photo-s/0f/f3/70/e0/caption.jpg", "https://media-cdn.tripadvisor.com/media/photo-s/0f/f3/73/18/2f.jpg"], "name": "Atelier Morimoto Xex", "address": "7-21-19 1 Field I.K.N. Roppongi Bldg., Roppongi, Minato 106-0032 Tokyo Prefecture", "phone": "03-3479-0065", "id": "6972545194100242", "rating": 4.5, "review_count": 197, "tags": ["Fine Dining", "Japanese", "Sushi", "Asian"], "price": "$$$$"}
  ]
  let items = temp.map((item) => ({ ...item, type: "restaurant"}))

  return (
    <Stack align="center" justify="flex-start">
      {items.map((item) => (
        <TableEntry item={item} />
      ))}
    </Stack>
  )
}