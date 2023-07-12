import { InstantSearch } from "react-instantsearch-hooks";
import { Hits } from "react-instantsearch-hooks-web/dist/es/ui/Hits";
import { SearchBox } from "react-instantsearch-hooks-web/dist/es/ui/SearchBox";
import TypesenseInstantsearchAdapter from "typesense-instantsearch-adapter";


const typesenseInstantSearchAdapter = new TypesenseInstantsearchAdapter({
  server: {
    apiKey: process.env.TYPESENSE_API_KEY,
    nodes: [{
      host: process.env.TYPESENSE_HOST,
      port: process.env.TYPESENSE_PORT,
      protocol: process.env.TYPESENSE_PROTOCOL
    }]
  },
  additionalSearchParameters: {
    query_by: "name"
  }
});
const searchClient = typesenseInstantSearchAdapter.searchClient;

export default function Home() {
  return (
    <InstantSearch searchClient={searchClient} indexName="restaurants">
      <SearchBox />
      <Hits />
    </InstantSearch>
  )
}