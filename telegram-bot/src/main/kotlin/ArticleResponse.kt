package goldenluk.readlaterbpt

data class ArticleResponse(
    val article_id: String,
    val user_article_id: String,
    val url: String,
    val type: String? = null
)