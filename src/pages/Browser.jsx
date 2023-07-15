import {
  Button,
  Collapse,
  createStyles
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import {
  InstantSearch,
  SearchBox
} from "react-instantsearch-hooks-web";
import TypesenseInstantsearchAdapter from "typesense-instantsearch-adapter";
import RefinementList from "components/search/RefinementList";
import Hits from "components/search/Hits";
import Pagination from "components/search/Pagination";


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
    height: "100%",
    display: "grid",
    [theme.fn.largerThan("sm")]: {
      gridTemplateColumns: "200px 1fr",
      gridTemplateAreas: `"sidebar body"`,
    },
    [theme.fn.smallerThan("sm")]: {
      gridTemplateRows: "min-content 1fr",
      gridTemplateAreas: `"sidebar" "body"`
    }
  },
  sidebar: {
    gridArea: "sidebar",
    minWidth: "0",
  },
  filters: {
    [theme.fn.smallerThan("sm")]: {
      display: "flex"
    }
  },
  body: {
    gridArea: "body",
    minWidth: "0",
    padding: [theme.spacing.lg],
    display: "flex",
    flexFlow: "column nowrap",
    backgroundColor: [theme.colorScheme === "dark" ? theme.colors.dark[8] : theme.colors.gray[0]]
  },
  refinementList: {
    height: "300px"
  }
}))

export default function Browser() {
  const { classes } = useStyles();
  const [opened, { toggle }] = useDisclosure(true);
  return (
    <InstantSearch searchClient={searchClient} indexName="restaurants">
      <div className={classes.layout}>
        <div className={classes.sidebar}>
          <Button
            onClick={toggle}
            variant="subtle"
            compact>
            {`${opened ? "Hide" : "Show"} filters`}
          </Button>
          <Collapse in={opened} className={classes.filters}>
            <RefinementList
              attribute="tags"
              operator="and"
              searchable={true}
              searchablePlaceholder="Search tags"
              limit={20}
              h={300}
            />
          </Collapse>
        </div>
        <div className={classes.body}>
          <SearchBox />
          <Hits />
          {/* <Pagination totalPages={10} padding={2} /> */}
        </div>
      </div>
    </InstantSearch>
  )
}