import {
  createStyles,
  Text
} from "@mantine/core";
import {
  InstantSearch,
  SearchBox,
  Hits
} from "react-instantsearch-hooks-web";
import TypesenseInstantsearchAdapter from "typesense-instantsearch-adapter";
import RefinementList from "../components/search/RefinementList";


const typesenseInstantSearchAdapter = new TypesenseInstantsearchAdapter({
  server: {
    apiKey: process.env.REACT_APP_TYPESENSE_API_KEY,
    nodes: [{
      host: process.env.REACT_APP_TYPESENSE_HOST,
      port: process.env.REACT_APP_TYPESENSE_PORT,
      protocol: process.env.REACT_APP_TYPESENSE_PROTOCOL
    }]
  },
  additionalSearchParameters: {
    query_by: "name"
  }
});
const searchClient = typesenseInstantSearchAdapter.searchClient;

const useStyles = createStyles((theme) => ({
  layout: {
    display: "grid",
    gridTemplateColumns: "200px 1fr",
    gridTemplateAreas: "sidebar body",
    "div": {
      outline: "1px solid red"
    }
  },
  sidebar: {
    gridArea: "sidebar",
    minWidth: "0"
  },
  body: {
    gridArea: "body"
  },
  refinementList: {
    // height: ""
  }
  

}))

export default function Home() {
  const { classes } = useStyles();
  return (
    <InstantSearch searchClient={searchClient} indexName="restaurants">
      <div className={classes.layout}>
        <div className={classes.sidebar}>
          <RefinementList
            className={classes.refinementList}
            attribute="tags"
            operator="and"
            searchable={true}
            searchablePlaceholder="Search"
            limit={1000}
          />
        </div>
        <div className={classes.body}>
          <SearchBox />
          <Hits />
        </div>
      </div>
    </InstantSearch>
  )
}