import { Carousel } from "@mantine/carousel";
import { Image, createStyles } from "@mantine/core";


const useStyles = createStyles((theme) => ({
  container: {
    height: "100%",
    width: "100%",
    display: "flex",
    borderRadius: [theme.radius.md],
    overflow: "hidden"
  },
  cardImage: {
    objectFit: "cover",
    height: "100%",
    width: "100%",
    borderRadius: [theme.radius.md]
  }
}));

export default function ImageCarousel({ urls, alt }) {
  const { classes } = useStyles();

  return (
    <div className={classes.container}>
      {urls.length === 0 ? (
        <Image width="100%" height="100%" sx={{ margin: "auto" }} withPlaceholder />
      ) : (
        <Carousel withIndicators height="100%" sx={{ flex: 1 }}>
          {urls.map((url) => (
            <Carousel.Slide key={url}><img className={classes.cardImage} src={url} alt={alt} /></Carousel.Slide>
          ))}
        </Carousel>
      )}
    </div>
  );
}