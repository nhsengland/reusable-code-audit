# Source: P23 STM for survey text — https://github.com/nhsx/stm-survey-text (R/main/functions.R)

prep_dataframe <- function(df, filter_sent = FALSE){
  df <- na.omit(df)
  if (filter_sent == TRUE){
    df <- df[(df$sentiment > 0.05) | (df$sentiment < -0.05),]
  }
  return(df)
}

clean_text <- function(data, StopWords, mintermfreq=2, lemma = TRUE, ngram = FALSE){
  t1 <- corpus(data$Response)
  docvars(t1, "doc_id") <- data$row_index
  docvars(t1) <- data

  t1 <- t1 %>% tolower()%>% textclean::replace_contraction()
  t2 <- gsub("[^[:alnum:][:space:]]","", t1)
  t2 <- gsub("[0-9]+", " ", t2)

  t4 <- quanteda::tokens(t2)
  if(ngram == TRUE){
    t4 <- tokens_ngrams(t4, n = c(1,2), concatenator = " ")
  }

  token <- tokens_remove(t4, pattern = StopWords)
  docfm <- dfm_trim(dfm(token), min_termfreq = mintermfreq)
  list("Tokens" = token, "DocMatrix" = docfm)
}
