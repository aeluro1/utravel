import {
  Button,
  Collapse,
  createStyles,
  useMantineTheme
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { InstantSearch } from "react-instantsearch-hooks-web";
import TypesenseInstantsearchAdapter from "typesense-instantsearch-adapter";
import RefinementList from "components/search/RefinementList";
import Hits from "components/search/Hits";
import Pagination from "components/search/Pagination";
import SearchBox from "components/search/SearchBox";
import { useEffect, useState } from "react";


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
    query_by: "name,address"
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
    },
    ">div": {
      outline: `1px solid ${theme.colors.gray[2]}`,
    }
  },
  sidebar: {
    gridArea: "sidebar",
    minWidth: "0",
    backgroundColor: [theme.colorScheme === "dark" ? theme.colors.dark[8] : theme.white],
    padding: `0 ${[theme.spacing.sm]}`
  },
  filters: {
    [theme.fn.smallerThan("sm")]: {
      display: "grid",
      gridTemplateColumns: "repeat(auto-fill, minmax(min(180px, 100%), 1fr))",
      gap: [theme.spacing.lg]
    }
  },
  body: {
    gridArea: "body",
    minWidth: "0",
    padding: [theme.spacing.lg],
    display: "grid",
    justifyItems: "center",
    gridAutoFlow: "column",
    gridTemplateRows: "repeat(3, min-content)",
    // gridAutoRows: "min-content", // Seems to make the grid fill in reverse direction
    gap: `calc(1 * ${[theme.spacing.lg]})`
  },
  refinementList: {
    height: "300px"
  },
  searchbar: {
    width: "min(80%, 800px)"
  }
}));

export default function Browser() {
  const { classes } = useStyles();
  const [opened, { toggle }] = useDisclosure(true);

  // // Dynamically collapse items upon window size change - WIP
  // const breakpoint = useMantineTheme().fn.smallerThan("sm").split("@media ")[1];
  // useEffect(() => {
  //   const mediaQuery = window.matchMedia(breakpoint);
  //   const handler = () => {
  //     console.log("triggered HERE");
  //     console.log(mediaQuery.matches);
  //     // const mediaQuery = window.matchMedia(breakpoint);
  //     if ((mediaQuery.matches && opened) || (!mediaQuery.matches && !opened)) {
  //       console.log("toggle");
  //       toggle();
  //     }
  //   }
  //   mediaQuery.addEventListener("change", handler);
  //   // return () => mediaQuery.removeEventListener("change", handler);
  // }, []);

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
          <Collapse in={opened}>
            <div className={classes.filters}>
              <RefinementList
                attribute="tags"
                operator="and"
                searchable
                searchablePlaceholder="Search tags"
                scrollable
                limit={30}
                h={280}
              />
              {/* <RefinementList
                attribute="price"
                operator="and"
                searchablePlaceholder="Filter price"
                limit={5}
                h={60}
              /> */}
            </div>
          </Collapse>
        </div>
        <div className={classes.body}>
          <div className={classes.searchbar}>
            <SearchBox placeholder="Search restaurants by name or location" />
          </div>
          <Hits />
          <Pagination siblings={1} boundaries={3} defaultValue={1} />
        </div>
      </div>
    </InstantSearch>
  );
}